from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


JobHandler = Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(slots=True)
class JobRuntime:
    _handlers: dict[str, JobHandler] = field(default_factory=dict)
    _queue: asyncio.Queue[tuple[str, dict[str, Any]]] = field(default_factory=asyncio.Queue)

    def register(self, name: str, handler: JobHandler) -> None:
        self._handlers[name] = handler

    async def enqueue(self, name: str, payload: dict[str, Any]) -> None:
        await self._queue.put((name, payload))

    async def run_once(self) -> bool:
        if self._queue.empty():
            return False
        name, payload = await self._queue.get()
        handler = self._handlers.get(name)
        if handler is None:
            raise KeyError(f"unknown job handler: {name}")
        await handler(payload)
        self._queue.task_done()
        return True

    async def drain(self) -> int:
        count = 0
        while await self.run_once():
            count += 1
        return count
