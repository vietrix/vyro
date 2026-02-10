from __future__ import annotations

import json

from vyro.observability.tracing import export_span, start_span


def test_start_span_parses_traceparent() -> None:
    span = start_span(
        "request",
        traceparent="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
    )
    assert span.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert span.parent_span_id == "00f067aa0ba902b7"


def test_export_span_returns_json_payload() -> None:
    span = start_span("db.query", attributes={"table": "users"})
    span.finish(status="ok")
    payload = json.loads(export_span(span))
    assert payload["type"] == "trace"
    assert payload["name"] == "db.query"
    assert payload["status"] == "ok"
    assert payload["attributes"]["table"] == "users"
