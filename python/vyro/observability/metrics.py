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
