from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows
from sentinel_ml.evaluate import evaluate


def test_model_smoke_on_synthetic_data() -> None:
    result = evaluate(generate_rows(SyntheticConfig(rows=3000, seed=11)))
    metrics = result["metrics"]
    assert metrics["recall"] >= 0.75
    assert metrics["cost_weighted_loss"] < 150

