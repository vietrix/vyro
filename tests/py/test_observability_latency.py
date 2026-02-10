from __future__ import annotations

from vyro.observability.latency import LatencyTracker


def test_latency_tracker_quantiles() -> None:
    tracker = LatencyTracker()
    for value in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        tracker.observe(value)
    summary = tracker.summary()
    assert summary["p50"] == 50
    assert summary["p95"] >= 90
    assert summary["p99"] >= 90


def test_latency_tracker_handles_empty_and_negative_values() -> None:
    tracker = LatencyTracker()
    tracker.observe(-5)
    assert tracker.summary() == {"p50": 0.0, "p95": 0.0, "p99": 0.0}


def test_latency_prometheus_render() -> None:
    tracker = LatencyTracker()
    tracker.observe(12.5)
    tracker.observe(25.0)
    rendered = tracker.render_prometheus()
    assert "# HELP vyro_request_latency_ms" in rendered
    assert 'vyro_request_latency_ms{quantile="0.95"}' in rendered
