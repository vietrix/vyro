from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any
from uuid import uuid4

import typer


@dataclass(slots=True)
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    started_at: datetime
    ended_at: datetime | None = None
    status: str = "ok"
    attributes: dict[str, Any] | None = None

    def finish(self, *, status: str = "ok") -> None:
        self.status = status
        self.ended_at = datetime.now(timezone.utc)


def start_span(name: str, *, traceparent: str | None = None, attributes: dict[str, Any] | None = None) -> Span:
    trace_id, parent_span_id = _extract_trace_context(traceparent)
    return Span(
        name=name,
        trace_id=trace_id,
        span_id=uuid4().hex[:16],
        parent_span_id=parent_span_id,
        started_at=datetime.now(timezone.utc),
        attributes=attributes or {},
    )


def export_span(span: Span) -> str:
    if span.ended_at is None:
        span.finish()
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "trace",
        "name": span.name,
        "trace_id": span.trace_id,
        "span_id": span.span_id,
        "parent_span_id": span.parent_span_id,
        "status": span.status,
        "started_at": span.started_at.isoformat(),
        "ended_at": span.ended_at.isoformat() if span.ended_at else None,
        "attributes": span.attributes or {},
    }
    return json.dumps(payload, ensure_ascii=False)


def emit_span(span: Span) -> None:
    typer.echo(export_span(span))


def _extract_trace_context(traceparent: str | None) -> tuple[str, str | None]:
    if not traceparent:
        return uuid4().hex, None
    parts = traceparent.strip().split("-")
    if len(parts) != 4:
        return uuid4().hex, None
    _, trace_id, parent_span_id, _ = parts
    if len(trace_id) != 32 or len(parent_span_id) != 16:
        return uuid4().hex, None
    return trace_id, parent_span_id
