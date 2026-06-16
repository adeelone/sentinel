from __future__ import annotations

import argparse
import json

from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows
from sentinel_ml.models.simple import HeuristicFraudModel


def confusion(scores: list[float], labels: list[int], threshold: float) -> dict[str, int]:
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


def evaluate(rows: list[dict[str, float | int]]) -> dict[str, object]:
    model = HeuristicFraudModel().fit(rows)
    scores = [model.predict_proba(row) for row in rows]
    labels = [int(row["Class"]) for row in rows]
    matrix = confusion(scores, labels, model.threshold)
    metrics = precision_recall(matrix)
    metrics["cost_weighted_loss"] = matrix["fp"] * 1.0 + matrix["fn"] * 25.0
    metrics["pr_auc_proxy"] = metrics["precision"] * metrics["recall"]
    return {"model": model.metadata(), "metrics": metrics, "confusion_matrix": matrix}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="synthetic")
    args = parser.parse_args()
    rows = generate_rows(SyntheticConfig(rows=5000)) if args.dataset == "synthetic" else []
    result = evaluate(rows)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
