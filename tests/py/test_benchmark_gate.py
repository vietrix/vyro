from __future__ import annotations

from vyro.benchmarks.gate import compare_benchmarks


def test_compare_benchmarks_detects_regression() -> None:
    baseline = {"results": {"routing": {"us_per_op": 1.0}}}
    current = {"results": {"routing": {"us_per_op": 2.0}}}
    regressions = compare_benchmarks(baseline, current, threshold_percent=50.0)
    assert len(regressions) == 1
    assert regressions[0].suite == "routing"


def test_compare_benchmarks_passes_when_within_threshold() -> None:
    baseline = {"results": {"json": {"us_per_op": 5.0}}}
    current = {"results": {"json": {"us_per_op": 6.0}}}
    regressions = compare_benchmarks(baseline, current, threshold_percent=25.0)
    assert regressions == []
