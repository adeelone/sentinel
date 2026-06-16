from __future__ import annotations

from typing import Protocol


class ExperimentTracker(Protocol):
    def log_metrics(self, run_id: str, metrics: dict[str, float]) -> None: ...
    def log_artifact(self, run_id: str, path: str) -> None: ...


class NoopTracker:
    def log_metrics(self, run_id: str, metrics: dict[str, float]) -> None:
        return None

    def log_artifact(self, run_id: str, path: str) -> None:
        return None

