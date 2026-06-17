from __future__ import annotations

from collections import defaultdict


class MetricsRegistry:
    def __init__(self) -> None:
        self.requests: dict[tuple[str, int], int] = defaultdict(int)
        self.latency_ms: list[float] = []
        self.model_load_count = 1

    def observe(self, path: str, status_code: int, latency_ms: float) -> None:
        self.requests[(path, status_code)] += 1
        self.latency_ms.append(latency_ms)

    def render(self) -> str:
        lines = []
        for (path, status_code), count in sorted(self.requests.items()):
            lines.append(
                f'sentinel_requests_total{{path="{path}",status="{status_code}"}} {count}'
            )
        if self.latency_ms:
            ordered = sorted(self.latency_ms)
            p50 = ordered[int((len(ordered) - 1) * 0.5)]
            p95 = ordered[int((len(ordered) - 1) * 0.95)]
            p99 = ordered[int((len(ordered) - 1) * 0.99)]
            lines.extend(
                [
                    f"sentinel_latency_ms_p50 {p50:.3f}",
                    f"sentinel_latency_ms_p95 {p95:.3f}",
                    f"sentinel_latency_ms_p99 {p99:.3f}",
                ]
            )
        lines.append(f"sentinel_model_load_count {self.model_load_count}")
        return "\n".join(lines) + "\n"


METRICS = MetricsRegistry()


def render_metrics() -> str:
    return METRICS.render()
