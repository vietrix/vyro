from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BenchmarkRegression:
    suite: str
    baseline_us_per_op: float
    current_us_per_op: float
    delta_percent: float


def load_benchmark_file(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "results" not in payload:
        raise ValueError(f"invalid benchmark file format: {path}")
    return payload


def compare_benchmarks(
    baseline: dict[str, object],
    current: dict[str, object],
    *,
    threshold_percent: float,
) -> list[BenchmarkRegression]:
    threshold = max(0.0, threshold_percent)
    baseline_results = _read_results(baseline)
    current_results = _read_results(current)

    regressions: list[BenchmarkRegression] = []
    for suite, base_metrics in baseline_results.items():
        current_metrics = current_results.get(suite)
        if current_metrics is None:
            regressions.append(
                BenchmarkRegression(
                    suite=suite,
                    baseline_us_per_op=float(base_metrics["us_per_op"]),
                    current_us_per_op=float("inf"),
                    delta_percent=float("inf"),
                )
            )
            continue
        baseline_us = float(base_metrics["us_per_op"])
        current_us = float(current_metrics["us_per_op"])
        if baseline_us <= 0:
            continue
        delta = ((current_us - baseline_us) / baseline_us) * 100.0
        if delta > threshold:
            regressions.append(
                BenchmarkRegression(
                    suite=suite,
                    baseline_us_per_op=baseline_us,
                    current_us_per_op=current_us,
                    delta_percent=delta,
                )
            )
    return regressions


def _read_results(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    results = payload.get("results")
    if not isinstance(results, dict):
        raise ValueError("benchmark payload missing 'results' object")
    output: dict[str, dict[str, object]] = {}
    for key, value in results.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        if "us_per_op" not in value:
            continue
        output[key] = value
    return output
