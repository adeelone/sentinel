from __future__ import annotations

import math


def population_stability_index(expected: list[float], actual: list[float]) -> float:
    total_expected = sum(expected) or 1
    total_actual = sum(actual) or 1
    score = 0.0
    for exp, act in zip(expected, actual, strict=True):
        exp_pct = max(exp / total_expected, 1e-6)
        act_pct = max(act / total_actual, 1e-6)
        score += (act_pct - exp_pct) * math.log(act_pct / exp_pct)
    return score

