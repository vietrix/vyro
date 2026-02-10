from __future__ import annotations

from vyro.observability.metrics import MetricsRegistry, create_default_registry


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
