from __future__ import annotations

import os

from sentinel_ml.tracking.base import ExperimentTracker, NoopTracker


def get_tracker() -> ExperimentTracker:
    if os.getenv("MLFLOW_TRACKING_URI"):
        return NoopTracker()
    return NoopTracker()

