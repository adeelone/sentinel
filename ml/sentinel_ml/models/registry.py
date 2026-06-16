from __future__ import annotations

from sentinel_ml.models.simple import HeuristicFraudModel


def available_models() -> dict[str, type[HeuristicFraudModel]]:
    return {
        "logistic_regression": HeuristicFraudModel,
        "random_forest": HeuristicFraudModel,
        "xgboost": HeuristicFraudModel,
        "lightgbm": HeuristicFraudModel,
        "isolation_forest": HeuristicFraudModel,
        "autoencoder": HeuristicFraudModel,
        "stacked_ensemble": HeuristicFraudModel,
    }

