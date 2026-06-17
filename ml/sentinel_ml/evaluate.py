from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows
from sentinel_ml.models.registry import available_models
from sentinel_ml.models.sklearn_models import FraudEstimator


@dataclass(frozen=True)
class CostConfig:
    false_positive: float = 1.0
    false_negative: float = 25.0


def confusion(scores: Sequence[float], labels: Sequence[int], threshold: float) -> dict[str, int]:
    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for score, label in zip(scores, labels, strict=True):
        pred = score >= threshold
        if pred and label:
            counts["tp"] += 1
        elif pred and not label:
            counts["fp"] += 1
        elif not pred and label:
            counts["fn"] += 1
        else:
            counts["tn"] += 1
    return counts


def precision_recall(counts: dict[str, int]) -> dict[str, float]:
    precision = counts["tp"] / max(counts["tp"] + counts["fp"], 1)
    recall = counts["tp"] / max(counts["tp"] + counts["fn"], 1)
    f2 = (5 * precision * recall) / max((4 * precision) + recall, 1e-9)
    return {"precision": precision, "recall": recall, "f2": f2}


def select_threshold(
    scores: Sequence[float],
    labels: Sequence[int],
    costs: CostConfig = CostConfig(),
) -> tuple[float, float]:
    candidates = sorted(set(float(score) for score in scores))
    if not candidates:
        return 0.5, 0.0
    best_threshold = candidates[0]
    best_cost = float("inf")
    for threshold in candidates:
        matrix = confusion(scores, labels, threshold)
        cost = matrix["fp"] * costs.false_positive + matrix["fn"] * costs.false_negative
        if cost < best_cost:
            best_cost = cost
            best_threshold = threshold
    return best_threshold, best_cost


def recall_at_precision(scores: Sequence[float], labels: Sequence[int], target: float) -> float:
    precision, recall, _ = precision_recall_curve(labels, scores)
    feasible = [float(rec) for prec, rec in zip(precision, recall, strict=True) if prec >= target]
    return max(feasible) if feasible else 0.0


def precision_at_recall(scores: Sequence[float], labels: Sequence[int], target: float) -> float:
    precision, recall, _ = precision_recall_curve(labels, scores)
    feasible = [float(prec) for prec, rec in zip(precision, recall, strict=True) if rec >= target]
    return max(feasible) if feasible else 0.0


def segment_metrics(
    rows: Sequence[dict[str, float | int]],
    scores: Sequence[float],
    labels: Sequence[int],
    threshold: float,
) -> dict[str, dict[str, float | int]]:
    buckets: dict[str, list[int]] = {"amount_low": [], "amount_mid": [], "amount_high": [], "night": [], "day": []}
    for index, row in enumerate(rows):
        amount = float(row["Amount"])
        hour = int(float(row["Time"]) // 3600) % 24
        if amount < 50:
            buckets["amount_low"].append(index)
        elif amount < 200:
            buckets["amount_mid"].append(index)
        else:
            buckets["amount_high"].append(index)
        buckets["night" if hour < 5 else "day"].append(index)

    result: dict[str, dict[str, float | int]] = {}
    for name, indexes in buckets.items():
        if not indexes:
            continue
        bucket_scores = [scores[index] for index in indexes]
        bucket_labels = [labels[index] for index in indexes]
        matrix = confusion(bucket_scores, bucket_labels, threshold)
        result[name] = {"rows": len(indexes), **precision_recall(matrix), **matrix}
    return result


def evaluate_model(
    model: FraudEstimator,
    train_rows: list[dict[str, float | int]],
    test_rows: list[dict[str, float | int]],
) -> dict[str, object]:
    model.fit(train_rows)
    train_scores = model.predict_scores(train_rows)
    train_labels = [int(row["Class"]) for row in train_rows]
    threshold, expected_cost = select_threshold(train_scores, train_labels)

    test_scores = model.predict_scores(test_rows)
    test_labels = [int(row["Class"]) for row in test_rows]
    matrix = confusion(test_scores, test_labels, threshold)
    point_metrics = precision_recall(matrix)
    has_both_classes = len(set(test_labels)) == 2
    metrics = {
        **point_metrics,
        "threshold": threshold,
        "cost_weighted_loss": matrix["fp"] + matrix["fn"] * CostConfig().false_negative,
        "expected_validation_cost": expected_cost,
        "pr_auc": float(average_precision_score(test_labels, test_scores)) if has_both_classes else 0.0,
        "roc_auc": float(roc_auc_score(test_labels, test_scores)) if has_both_classes else 0.0,
        "brier_score": float(brier_score_loss(test_labels, np.clip(test_scores, 0, 1))) if has_both_classes else 0.0,
        "recall_at_precision_0_5": recall_at_precision(test_scores, test_labels, 0.5),
        "recall_at_precision_0_7": recall_at_precision(test_scores, test_labels, 0.7),
        "recall_at_precision_0_9": recall_at_precision(test_scores, test_labels, 0.9),
        "precision_at_recall_0_5": precision_at_recall(test_scores, test_labels, 0.5),
        "precision_at_recall_0_7": precision_at_recall(test_scores, test_labels, 0.7),
        "precision_at_recall_0_9": precision_at_recall(test_scores, test_labels, 0.9),
    }
    return {
        "model": model.metadata(),
        "metrics": metrics,
        "confusion_matrix": matrix,
        "segments": segment_metrics(test_rows, test_scores, test_labels, threshold),
        "sample_explanation": model.contributions(test_rows[0]) if test_rows else [],
    }


def evaluate(rows: list[dict[str, float | int]], model_names: list[str] | None = None) -> dict[str, object]:
    labels = [int(row["Class"]) for row in rows]
    train_rows, test_rows = train_test_split(
        rows,
        test_size=0.3,
        random_state=42,
        stratify=labels,
    )
    registry = available_models()
    selected = model_names or list(registry)
    models = {
        name: evaluate_model(registry[name](), list(train_rows), list(test_rows))
        for name in selected
        if name in registry
    }
    best_name = min(
        models,
        key=lambda name: float(models[name]["metrics"]["cost_weighted_loss"]),  # type: ignore[index]
    )
    return {"best_model": best_name, "models": models}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="synthetic")
    parser.add_argument("--models", default="logistic_regression,random_forest,isolation_forest")
    args = parser.parse_args()
    rows = generate_rows(SyntheticConfig(rows=8000)) if args.dataset == "synthetic" else []
    result = evaluate(rows, [name.strip() for name in args.models.split(",") if name.strip()])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
