from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from .task_trace import attach_task_trace, detach_task_trace, task_trace_scope


JobHandler = Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(slots=True)
class DeadLetterEntry:
    job_name: str
    payload: dict[str, Any]
    attempts: int
    error: str
    trace_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class DeadLetterQueue:
    _items: list[DeadLetterEntry] = field(default_factory=list)

    def push(self, entry: DeadLetterEntry) -> None:
        self._items.append(entry)

    def items(self) -> list[DeadLetterEntry]:
        return list(self._items)


@dataclass(slots=True)
class JobRetryExecutor:
    max_retries: int = 3
    dead_letter_queue: DeadLetterQueue = field(default_factory=DeadLetterQueue)

    async def run(
        self,
        job_name: str,
        payload: dict[str, Any],
        handler: JobHandler,
        *,
        trace_id: str | None = None,
    ) -> bool:
        traced_payload = attach_task_trace(payload, trace_id=trace_id)
        clean_payload, resolved_trace_id = detach_task_trace(traced_payload)
        attempts = 0
        last_error: Exception | None = None
        while attempts <= self.max_retries:
            try:
                attempts += 1
                with task_trace_scope(resolved_trace_id):
                    await handler(clean_payload)
                return True
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        self.dead_letter_queue.push(
            DeadLetterEntry(
                job_name=job_name,
                payload=clean_payload,
                attempts=attempts,
                error=str(last_error) if last_error is not None else "unknown error",
                trace_id=resolved_trace_id,
            )
        )
        return False
