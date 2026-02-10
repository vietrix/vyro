from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SSEEvent:
    data: str
    event: str | None = None
    id: str | None = None
    retry_ms: int | None = None

    def encode(self) -> str:
        lines: list[str] = []
        if self.id is not None:
            lines.append(f"id: {self.id}")
        if self.event is not None:
            lines.append(f"event: {self.event}")
        if self.retry_ms is not None:
            lines.append(f"retry: {self.retry_ms}")
        for chunk in self.data.splitlines() or [""]:
            lines.append(f"data: {chunk}")
        return "\n".join(lines) + "\n\n"


@dataclass(slots=True)
class SSEResponse:
    events: list[SSEEvent] = field(default_factory=list)
    status: int = 200
    headers: dict[str, str] = field(
        default_factory=lambda: {
            "content-type": "text/event-stream; charset=utf-8",
            "cache-control": "no-cache",
            "connection": "keep-alive",
        }
    )

    def send(
        self,
        data: str,
        *,
        event: str | None = None,
        id: str | None = None,
        retry_ms: int | None = None,
    ) -> None:
        self.events.append(SSEEvent(data=data, event=event, id=id, retry_ms=retry_ms))

    def body_bytes(self) -> bytes:
        payload = "".join(event.encode() for event in self.events)
        return payload.encode("utf-8")

    def as_tuple(self) -> tuple[Any, int, dict[str, str]]:
        return self.body_bytes(), self.status, self.headers
