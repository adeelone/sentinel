from __future__ import annotations

import math
import time
from pathlib import Path
from threading import RLock
from typing import Any, cast

import joblib  # type: ignore[import-untyped]

from app.core.config import settings
from app.schemas import Contribution, ScoreRequest, ScoreResponse
from app.scoring.artifacts import download_bundle


class FallbackModel:
    model_name = "local-demo-fallback"
    threshold = 0.72
    metrics: dict[str, object] = {}
    run_id = "local"

    def predict_scores(self, rows: list[dict[str, float | int]]) -> list[float]:
        scores = []
        for row in rows:
            linear = (
                float(row["V14"]) * 0.28
                + float(row["V10"]) * 0.22
                + float(row["V17"]) * 0.2
                + min(float(row["Amount"]), 500) / 500 * 0.18
                - 1.3
            )
            scores.append(1 / (1 + math.exp(-linear)))
        return scores

    def contributions(
        self, row: dict[str, float | int], top_n: int = 5
    ) -> list[dict[str, float | str]]:
        values = {
            "V14": float(row["V14"]) * 0.28,
            "V10": float(row["V10"]) * 0.22,
            "V17": float(row["V17"]) * 0.2,
            "Amount": min(float(row["Amount"]), 500) / 500 * 0.18,
        }
        return [
            {
                "feature": key,
                "value": round(value, 6),
                "direction": "positive" if value >= 0 else "negative",
            }
            for key, value in sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)[
                :top_n
            ]
        ]


class ModelManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = RLock()
        self._mtime = -1.0
        self._model: Any = FallbackModel()
        self._last_remote_check = 0.0
        self.threshold = self._model.threshold
        self.metrics: dict[str, object] = {}
        self.run_id = "local"
        self.reload()

    @property
    def model_name(self) -> str:
        return str(self._model.model_name)

    @property
    def using_bundle(self) -> bool:
        return self._mtime >= 0

    def reload(self) -> bool:
        now = time.monotonic()
        if now - self._last_remote_check >= 60:
            download_bundle(self.path)
            self._last_remote_check = now
        if not self.path.exists():
            return False
        mtime = self.path.stat().st_mtime
        if mtime == self._mtime:
            return False
        with self._lock:
            bundle = joblib.load(self.path)
            self._model = bundle["model"]
            metrics_block = bundle.get("metrics", {})
            self.metrics = dict(metrics_block.get("metrics", {}))
            self.threshold = float(cast(float | int | str, self.metrics.get("threshold", 0.5)))
            self.run_id = str(bundle.get("run_id", "unknown"))
            self._mtime = mtime
        return True

    def score(self, payload: ScoreRequest) -> ScoreResponse:
        self.reload()
        row = payload.model_dump()
        score = float(self._model.predict_scores([row])[0])
        try:
            raw = self._model.contributions(row)
            contributions = [Contribution.model_validate(item) for item in raw]
        except Exception:
            contributions = None
        strongest = ", ".join(item.feature for item in (contributions or [])[:3])
        rationale = (
            f"Strongest model signals: {strongest}"
            if strongest
            else "Model explanation unavailable"
        )
        return ScoreResponse(
            score=round(score, 6),
            label="flagged" if score >= self.threshold else "clear",
            threshold=self.threshold,
            contributions=contributions,
            model_version=f"{self.model_name}:{self.run_id}",
            rationale=rationale,
        )


ACTIVE_MODEL = ModelManager(settings.model_bundle_path)


def score_transaction(payload: ScoreRequest) -> ScoreResponse:
    return ACTIVE_MODEL.score(payload)
