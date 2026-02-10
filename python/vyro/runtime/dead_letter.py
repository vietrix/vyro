from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable


JobHandler = Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(slots=True)
class DeadLetterEntry:
    job_name: str
    payload: dict[str, Any]
    attempts: int
    error: str
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

    async def run(self, job_name: str, payload: dict[str, Any], handler: JobHandler) -> bool:
        attempts = 0
        last_error: Exception | None = None
        while attempts <= self.max_retries:
            try:
                attempts += 1
                await handler(payload)
                return True
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        self.dead_letter_queue.push(
            DeadLetterEntry(
                job_name=job_name,
                payload=payload,
                attempts=attempts,
                error=str(last_error) if last_error is not None else "unknown error",
            )
        )
        return False
