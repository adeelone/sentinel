from sentinel_ml.features.transformers import cyclical_time, robust_scale, robust_stats, winsorize


def test_transformers_are_stable() -> None:
    stats = robust_stats([1, 2, 3, 4, 5])
    assert robust_scale(3, stats) == 0
    encoded = cyclical_time(3600)
    assert set(encoded) == {"hour_sin", "hour_cos", "week_sin", "week_cos"}
    assert winsorize(10, 0, 5) == 5

