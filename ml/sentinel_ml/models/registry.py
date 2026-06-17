from __future__ import annotations

from typing import Callable

from sentinel_ml.models.sklearn_models import (
    FraudEstimator,
    IsolationForestModel,
    logistic_regression,
    random_forest,
)


def available_models() -> dict[str, Callable[[], FraudEstimator]]:
    return {
        "logistic_regression": logistic_regression,
        "random_forest": random_forest,
        "isolation_forest": IsolationForestModel,
    }
