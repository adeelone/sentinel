from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class HeuristicFraudModel:
    threshold: float = 0.72
    model_name: str = "heuristic-smoke"

    def fit(self, rows: list[dict[str, float | int]]) -> "HeuristicFraudModel":
        scored = [(self._raw_score(row), int(row["Class"])) for row in rows]
        candidates = sorted({score for score, _ in scored})
        best_threshold = self.threshold
        best_cost = float("inf")
        for threshold in candidates:
            fp = sum(1 for score, label in scored if score >= threshold and label == 0)
            fn = sum(1 for score, label in scored if score < threshold and label == 1)
            cost = fp + fn * 25
            if cost < best_cost:
                best_cost = cost
                best_threshold = threshold
        self.threshold = best_threshold
        return self

    def predict_proba(self, row: dict[str, float | int]) -> float:
        return min(max(self._raw_score(row), 0.0), 1.0)

    def metadata(self) -> dict[str, str | float]:
        return {"name": self.model_name, "threshold": self.threshold}

    def contributions(self, row: dict[str, float | int], top_n: int = 4) -> list[dict[str, float | str]]:
        weighted = {
            "V14": float(row["V14"]) * 0.28,
            "V10": float(row["V10"]) * 0.22,
            "V17": float(row["V17"]) * 0.2,
            "Amount": math.log1p(float(row["Amount"])) * 0.08,
            "Time": self._night_factor(float(row["Time"])) * 0.12,
        }
        ordered = sorted(weighted.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n]
        return [{"feature": name, "value": round(value, 6), "direction": "positive" if value >= 0 else "negative"} for name, value in ordered]

    def _raw_score(self, row: dict[str, float | int]) -> float:
        linear = (
            float(row["V14"]) * 0.28
            + float(row["V10"]) * 0.22
            + float(row["V17"]) * 0.2
            + math.log1p(float(row["Amount"])) * 0.08
            + self._night_factor(float(row["Time"])) * 0.12
            - 1.3
        )
        return 1 / (1 + math.exp(-linear))

    @staticmethod
    def _night_factor(seconds: float) -> float:
        hour = int(seconds // 3600) % 24
        return 1.0 if hour < 5 else 0.0
