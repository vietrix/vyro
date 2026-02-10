from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CounterMetric:
    name: str
    description: str
    value: int = 0
    labels: dict[str, str] = field(default_factory=dict)

    def inc(self, amount: int = 1) -> None:
        self.value += amount


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, CounterMetric] = {}

    def counter(
        self,
        name: str,
        description: str,
        *,
        labels: dict[str, str] | None = None,
    ) -> CounterMetric:
        metric = self._counters.get(name)
        if metric is None:
            metric = CounterMetric(
                name=name,
                description=description,
                labels=dict(labels or {}),
            )
            self._counters[name] = metric
        return metric

    def render_prometheus(self) -> str:
        lines: list[str] = []
        for metric in self._counters.values():
            lines.append(f"# HELP {metric.name} {metric.description}")
            lines.append(f"# TYPE {metric.name} counter")
            if metric.labels:
                label_text = ",".join(f'{k}="{v}"' for k, v in sorted(metric.labels.items()))
                lines.append(f"{metric.name}{{{label_text}}} {metric.value}")
            else:
                lines.append(f"{metric.name} {metric.value}")
        return "\n".join(lines) + ("\n" if lines else "")


def create_default_registry() -> MetricsRegistry:
    registry = MetricsRegistry()
    registry.counter(
        "vyro_requests_total",
        "Total number of requests processed by Vyro runtime",
    )
    return registry


@dataclass(slots=True)
class ThroughputTracker:
    _counts: dict[tuple[str, str], int] = field(default_factory=dict)

    def observe(self, method: str, route: str, amount: int = 1) -> None:
        key = (method.upper(), route)
        self._counts[key] = self._counts.get(key, 0) + amount

    def value(self, method: str, route: str) -> int:
        return self._counts.get((method.upper(), route), 0)

    def render_prometheus(self, metric_name: str = "vyro_route_requests_total") -> str:
        lines = [f"# HELP {metric_name} Number of requests per route"]
        lines.append(f"# TYPE {metric_name} counter")
        for (method, route), value in sorted(self._counts.items()):
            lines.append(
                f'{metric_name}{{method="{method}",route="{route}"}} {value}'
            )
        return "\n".join(lines) + "\n"
