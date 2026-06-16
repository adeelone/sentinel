from sentinel_ml.data.synthetic import CSV_HEADER, SyntheticConfig, fraud_ratio, generate_rows


def test_synthetic_shape_and_imbalance() -> None:
    rows = generate_rows(SyntheticConfig(rows=3000, seed=7))
    assert len(rows) == 3000
    assert set(CSV_HEADER).issubset(rows[0])
    assert 0.001 <= fraud_ratio(rows) <= 0.003

