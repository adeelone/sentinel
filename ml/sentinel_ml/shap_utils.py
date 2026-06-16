from __future__ import annotations

from sentinel_ml.models.simple import HeuristicFraudModel


def explain(model: HeuristicFraudModel, row: dict[str, float | int]) -> list[dict[str, float | str]]:
    try:
        return model.contributions(row)
    except Exception:
        return []

