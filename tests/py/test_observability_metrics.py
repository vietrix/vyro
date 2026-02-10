from __future__ import annotations

from vyro.observability.metrics import MetricsRegistry, ThroughputTracker, create_default_registry


def test_metrics_counter_increment_and_render() -> None:
    registry = MetricsRegistry()
    metric = registry.counter("vyro_requests_total", "Total requests")
    metric.inc()
    metric.inc(2)
    rendered = registry.render_prometheus()
    assert "# HELP vyro_requests_total Total requests" in rendered
    assert "# TYPE vyro_requests_total counter" in rendered
    assert "vyro_requests_total 3" in rendered


def test_metrics_render_includes_labels() -> None:
    registry = MetricsRegistry()
    metric = registry.counter(
        "vyro_requests_by_status_total",
        "Requests by status",
        labels={"status": "200", "method": "GET"},
    )
    metric.inc()
    rendered = registry.render_prometheus()
    assert 'vyro_requests_by_status_total{method="GET",status="200"} 1' in rendered


def test_default_registry_has_core_metric() -> None:
    registry = create_default_registry()
    rendered = registry.render_prometheus()
    assert "vyro_requests_total" in rendered


def test_throughput_tracker_counts_per_route() -> None:
    tracker = ThroughputTracker()
    tracker.observe("get", "/users/{id}")
    tracker.observe("GET", "/users/{id}", amount=2)
    tracker.observe("post", "/users")
    assert tracker.value("GET", "/users/{id}") == 3
    assert tracker.value("POST", "/users") == 1


def test_throughput_tracker_renders_prometheus() -> None:
    tracker = ThroughputTracker()
    tracker.observe("GET", "/healthz")
    rendered = tracker.render_prometheus()
    assert "# HELP vyro_route_requests_total" in rendered
    assert 'vyro_route_requests_total{method="GET",route="/healthz"} 1' in rendered
