from __future__ import annotations

from dataclasses import dataclass, field
from inspect import isawaitable
from typing import Any, Awaitable, Callable, Generic, TypeVar


TPayload = TypeVar("TPayload")
EventHandler = Callable[["InternalEvent[Any]"], Awaitable[None] | None]


@dataclass(frozen=True, slots=True)
class InternalEvent(Generic[TPayload]):
    name: str
    payload: TPayload
    trace_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class InternalEventBus:
    _subscribers: dict[str, list[EventHandler]] = field(default_factory=dict)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        handlers = self._subscribers.setdefault(event_name, [])
        handlers.append(handler)

    def subscribers(self, event_name: str) -> tuple[EventHandler, ...]:
        return tuple(self._subscribers.get(event_name, []))

    async def publish(
        self,
        event_name: str,
        payload: Any,
        *,
        trace_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> int:
        handlers = self._subscribers.get(event_name, [])
        if not handlers:
            return 0

        event = InternalEvent[Any](
            name=event_name,
            payload=payload,
            trace_id=trace_id,
            metadata=dict(metadata or {}),
        )
        for handler in handlers:
            result = handler(event)
            if isawaitable(result):
                await result
        return len(handlers)
