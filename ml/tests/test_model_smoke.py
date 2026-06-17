from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows
from sentinel_ml.evaluate import evaluate


def test_model_smoke_on_synthetic_data() -> None:
    result = evaluate(
        generate_rows(SyntheticConfig(rows=3000, seed=11)),
        model_names=["logistic_regression", "random_forest"],
    )
    assert result["best_model"] in {"logistic_regression", "random_forest"}
    for model in result["models"].values():
        metrics = model["metrics"]
        assert "pr_auc" in metrics
        assert "roc_auc" in metrics
        assert "brier_score" in metrics
        assert metrics["cost_weighted_loss"] < 250
