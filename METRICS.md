# Metrics

Accuracy is not used as a primary metric because the dataset is severely imbalanced.

Primary metrics:

- PR-AUC.
- ROC-AUC.
- Recall at fixed precision: 0.5, 0.7, 0.9.
- Precision at fixed recall: 0.5, 0.7, 0.9.
- F2 score.
- Brier score.
- Cost-weighted loss.

Expected cost is computed as:

```text
cost = false_positives * fp_cost + false_negatives * fn_cost
```

The default threshold minimizes validation cost with a higher false-negative cost.

