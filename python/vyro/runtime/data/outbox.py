from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Protocol


Publisher = Callable[[str, dict[str, Any]], Awaitable[None]]


@dataclass(slots=True)
class OutboxMessage:
    id: int
    topic: str
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: datetime | None = None


class OutboxStore(Protocol):
    def append(self, topic: str, payload: dict[str, Any]) -> OutboxMessage:
        ...

    def pending(self) -> list[OutboxMessage]:
        ...

    def mark_sent(self, message_id: int) -> None:
        ...


@dataclass(slots=True)
class InMemoryOutboxStore:
    _messages: list[OutboxMessage] = field(default_factory=list)
    _sequence: int = 0

    def append(self, topic: str, payload: dict[str, Any]) -> OutboxMessage:
        self._sequence += 1
        message = OutboxMessage(id=self._sequence, topic=topic, payload=dict(payload))
        self._messages.append(message)
        return message

    def pending(self) -> list[OutboxMessage]:
        return [m for m in self._messages if m.sent_at is None]

    def mark_sent(self, message_id: int) -> None:
        for message in self._messages:
            if message.id == message_id:
                message.sent_at = datetime.now(timezone.utc)
                return
        raise KeyError(f"unknown outbox message: {message_id}")


@dataclass(slots=True)
class OutboxPatternHelper:
    store: OutboxStore = field(default_factory=InMemoryOutboxStore)

    def stage(self, topic: str, payload: dict[str, Any]) -> OutboxMessage:
        return self.store.append(topic, payload)

    async def flush(self, publisher: Publisher, *, limit: int | None = None) -> int:
        pending = self.store.pending()
        if limit is not None:
            pending = pending[: max(limit, 0)]
        delivered = 0
        for message in pending:
            await publisher(message.topic, dict(message.payload))
            self.store.mark_sent(message.id)
            delivered += 1
        return delivered
