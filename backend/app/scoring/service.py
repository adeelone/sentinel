from __future__ import annotations

from app.schemas import Contribution, ScoreRequest, ScoreResponse


class RuntimeModel:
    model_name = "sentinel-synthetic-v0"
    threshold = 0.72

    def predict(self, payload: ScoreRequest) -> float:
        linear = (
            payload.V14 * 0.28
            + payload.V10 * 0.22
            + payload.V17 * 0.2
            + min(payload.Amount, 500) / 500 * 0.18
            + (0.12 if int(payload.Time // 3600) % 24 < 5 else 0)
            - 1.3
        )
        return 1 / (1 + pow(2.718281828, -linear))


ACTIVE_MODEL = RuntimeModel()


def score_transaction(payload: ScoreRequest) -> ScoreResponse:
    score = ACTIVE_MODEL.predict(payload)
    try:
        contributions = [
            Contribution(feature="V14", value=round(payload.V14 * 0.28, 6), direction="positive" if payload.V14 >= 0 else "negative"),
            Contribution(feature="V10", value=round(payload.V10 * 0.22, 6), direction="positive" if payload.V10 >= 0 else "negative"),
            Contribution(feature="V17", value=round(payload.V17 * 0.2, 6), direction="positive" if payload.V17 >= 0 else "negative"),
            Contribution(feature="Amount", value=round(min(payload.Amount, 500) / 500 * 0.18, 6), direction="positive"),
        ]
    except Exception:
        contributions = None
    rationale = (
        "High V14, unusual Amount, and past-midnight timing"
        if score >= ACTIVE_MODEL.threshold
        else "Below active operating threshold"
    )
    return ScoreResponse(
        score=round(score, 6),
        label="flagged" if score >= ACTIVE_MODEL.threshold else "clear",
        threshold=ACTIVE_MODEL.threshold,
        contributions=contributions,
        model_version=ACTIVE_MODEL.model_name,
        rationale=rationale,
    )
