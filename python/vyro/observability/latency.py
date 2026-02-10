from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LatencyTracker:
    samples_ms: list[float] = field(default_factory=list)

    def observe(self, value_ms: float) -> None:
        if value_ms < 0:
            return
        self.samples_ms.append(value_ms)

    def quantile(self, q: float) -> float:
        if not self.samples_ms:
            return 0.0
        if q <= 0:
            return min(self.samples_ms)
        if q >= 1:
            return max(self.samples_ms)
        ordered = sorted(self.samples_ms)
        idx = int(round((len(ordered) - 1) * q))
        return ordered[idx]

    def summary(self) -> dict[str, float]:
        return {
            "p50": self.quantile(0.50),
            "p95": self.quantile(0.95),
            "p99": self.quantile(0.99),
        }

    def render_prometheus(self, metric_prefix: str = "vyro_request_latency_ms") -> str:
        stats = self.summary()
        lines = [f"# HELP {metric_prefix} Request latency quantiles in milliseconds"]
        lines.append(f"# TYPE {metric_prefix} gauge")
        lines.append(f'{metric_prefix}{{quantile="0.50"}} {stats["p50"]}')
        lines.append(f'{metric_prefix}{{quantile="0.95"}} {stats["p95"]}')
        lines.append(f'{metric_prefix}{{quantile="0.99"}} {stats["p99"]}')
        return "\n".join(lines) + "\n"
