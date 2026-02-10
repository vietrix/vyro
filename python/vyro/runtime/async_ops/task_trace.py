from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Iterator
from uuid import uuid4


TRACE_ID_FIELD = "__vyro_trace_id"
_current_trace_id: ContextVar[str | None] = ContextVar("vyro_current_task_trace_id", default=None)


@dataclass(frozen=True, slots=True)
class TaskTraceContext:
    trace_id: str


def create_trace_id() -> str:
    return uuid4().hex


def current_task_trace() -> TaskTraceContext | None:
    trace_id = _current_trace_id.get()
    if trace_id is None:
        return None
    return TaskTraceContext(trace_id=trace_id)


def attach_task_trace(payload: dict[str, object], trace_id: str | None = None) -> dict[str, object]:
    result = dict(payload)
    result[TRACE_ID_FIELD] = trace_id or create_trace_id()
    return result


def detach_task_trace(payload: dict[str, object]) -> tuple[dict[str, object], str]:
    result = dict(payload)
    trace_id_raw = result.pop(TRACE_ID_FIELD, None)
    trace_id = trace_id_raw if isinstance(trace_id_raw, str) and trace_id_raw else create_trace_id()
    return result, trace_id


@contextmanager
def task_trace_scope(trace_id: str) -> Iterator[None]:
    token: Token[str | None] = _current_trace_id.set(trace_id)
    try:
        yield
    finally:
        _current_trace_id.reset(token)
