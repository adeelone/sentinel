from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler


FEATURE_COLUMNS = ["Time", "Amount", *[f"V{i}" for i in range(1, 29)]]


class FraudEstimator(Protocol):
    model_name: str

    def fit(self, rows: list[dict[str, float | int]]) -> "FraudEstimator": ...
    def predict_scores(self, rows: list[dict[str, float | int]]) -> list[float]: ...
    def metadata(self) -> dict[str, str | float]: ...
    def contributions(self, row: dict[str, float | int], top_n: int = 5) -> list[dict[str, float | str]]: ...


def matrix_from_rows(rows: list[dict[str, float | int]]) -> np.ndarray:
    return np.array([[float(row[column]) for column in FEATURE_COLUMNS] for row in rows], dtype=float)


def labels_from_rows(rows: list[dict[str, float | int]]) -> np.ndarray:
    return np.array([int(row["Class"]) for row in rows], dtype=int)


@dataclass
class SklearnClassifierModel:
    model_name: str
    estimator: Pipeline

    def fit(self, rows: list[dict[str, float | int]]) -> "SklearnClassifierModel":
        self.estimator.fit(matrix_from_rows(rows), labels_from_rows(rows))
        return self

    def predict_scores(self, rows: list[dict[str, float | int]]) -> list[float]:
        probabilities = self.estimator.predict_proba(matrix_from_rows(rows))
        return cast(list[float], probabilities[:, 1].astype(float).tolist())

    def metadata(self) -> dict[str, str | float]:
        return {"name": self.model_name, "type": "sklearn_classifier"}

    def contributions(self, row: dict[str, float | int], top_n: int = 5) -> list[dict[str, float | str]]:
        model = self.estimator.named_steps["model"]
        values = np.array([float(row[column]) for column in FEATURE_COLUMNS], dtype=float)
        if hasattr(model, "coef_"):
            weights = model.coef_[0]
            raw = dict(zip(FEATURE_COLUMNS, values * weights, strict=True))
        elif hasattr(model, "feature_importances_"):
            raw = dict(zip(FEATURE_COLUMNS, values * model.feature_importances_, strict=True))
        else:
            raw = {}
        ordered = sorted(raw.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n]
        return [
            {
                "feature": feature,
                "value": round(float(value), 6),
                "direction": "positive" if value >= 0 else "negative",
            }
            for feature, value in ordered
        ]


@dataclass
class IsolationForestModel:
    model_name: str = "isolation_forest"

    def __post_init__(self) -> None:
        self.estimator = Pipeline(
            [
                ("scale", RobustScaler()),
                ("model", IsolationForest(n_estimators=80, contamination=0.01, random_state=42)),
            ]
        )

    def fit(self, rows: list[dict[str, float | int]]) -> "IsolationForestModel":
        self.estimator.fit(matrix_from_rows(rows))
        return self

    def predict_scores(self, rows: list[dict[str, float | int]]) -> list[float]:
        raw_scores = -self.estimator.decision_function(matrix_from_rows(rows))
        low = float(np.min(raw_scores))
        high = float(np.max(raw_scores))
        if high - low < 1e-9:
            return [0.0 for _ in raw_scores]
        return cast(list[float], ((raw_scores - low) / (high - low)).astype(float).tolist())

    def metadata(self) -> dict[str, str | float]:
        return {"name": self.model_name, "type": "sklearn_unsupervised"}

    def contributions(self, row: dict[str, float | int], top_n: int = 5) -> list[dict[str, float | str]]:
        values = {column: float(row[column]) for column in FEATURE_COLUMNS}
        ordered = sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n]
        return [
            {
                "feature": feature,
                "value": round(value, 6),
                "direction": "positive" if value >= 0 else "negative",
            }
            for feature, value in ordered
        ]


def logistic_regression() -> SklearnClassifierModel:
    return SklearnClassifierModel(
        model_name="logistic_regression",
        estimator=Pipeline(
            [
                ("scale", RobustScaler()),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1000,
                        random_state=42,
                    ),
                ),
            ]
        ),
    )


def random_forest() -> SklearnClassifierModel:
    return SklearnClassifierModel(
        model_name="random_forest",
        estimator=Pipeline(
            [
                ("scale", RobustScaler()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=8,
                        class_weight="balanced_subsample",
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
    )
