from __future__ import annotations

from pathlib import Path

import joblib  # type: ignore[import-untyped]

from app.jobs import queue
from app.schemas import ScoreRequest
from app.scoring.service import ModelManager


class FakeModel:
    model_name = "test_model"

    def predict_scores(self, rows):
        return [0.8 for _ in rows]

    def contributions(self, row, top_n=5):
        return [{"feature": "V14", "value": 0.5, "direction": "positive"}]


class FakeRedis:
    def __init__(self) -> None:
        self.hashes: dict[str, dict[str, str]] = {}
        self.items: list[str] = []

    def hset(self, key: str, mapping: dict[str, str]) -> None:
        self.hashes[key] = mapping

    def rpush(self, key: str, value: str) -> None:
        assert key == "sentinel:jobs"
        self.items.append(value)


def test_model_manager_loads_a_versioned_bundle() -> None:
    bundle = Path("data/test-model-bundle.joblib")
    bundle.parent.mkdir(exist_ok=True)
    try:
        joblib.dump(
            {
                "model": FakeModel(),
                "run_id": "run-123",
                "metrics": {"metrics": {"threshold": 0.7, "pr_auc": 0.9}},
            },
            bundle,
        )
        manager = ModelManager(bundle)
        result = manager.score(ScoreRequest(Time=1, Amount=10, V14=2))
        assert manager.using_bundle
        assert result.label == "flagged"
        assert result.model_version == "test_model:run-123"
        assert result.contributions and result.contributions[0].feature == "V14"
    finally:
        bundle.unlink(missing_ok=True)


def test_retrain_enqueue_records_status(monkeypatch) -> None:
    redis = FakeRedis()
    monkeypatch.setattr(queue, "redis_client", lambda: redis)
    job_id = queue.enqueue_retrain()
    assert redis.hashes[f"sentinel:job:{job_id}"]["status"] == "queued"
    assert job_id in redis.items[0]
