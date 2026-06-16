from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RobustStats:
    median: float
    iqr: float


def robust_stats(values: list[float]) -> RobustStats:
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid]
    q1 = ordered[len(ordered) // 4]
    q3 = ordered[(len(ordered) * 3) // 4]
    return RobustStats(median=median, iqr=max(q3 - q1, 1e-9))


def robust_scale(value: float, stats: RobustStats) -> float:
    return (value - stats.median) / stats.iqr


def cyclical_time(seconds: float) -> dict[str, float]:
    day_fraction = (seconds % 86400) / 86400
    week_fraction = (seconds % (86400 * 7)) / (86400 * 7)
    return {
        "hour_sin": math.sin(math.tau * day_fraction),
        "hour_cos": math.cos(math.tau * day_fraction),
        "week_sin": math.sin(math.tau * week_fraction),
        "week_cos": math.cos(math.tau * week_fraction),
    }


def winsorize(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)

