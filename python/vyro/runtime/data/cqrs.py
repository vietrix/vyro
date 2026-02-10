from __future__ import annotations

from dataclasses import dataclass
from inspect import isawaitable
from typing import Any, Awaitable, Callable


CommandHandler = Callable[[dict[str, Any]], Awaitable[None] | None]
QueryHandler = Callable[[dict[str, Any]], Awaitable[Any] | Any]


class CQRSError(RuntimeError):
    pass


class DuplicateHandlerError(CQRSError):
    pass


class UnknownHandlerError(CQRSError):
    pass


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    name: str
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class QueryEnvelope:
    name: str
    payload: dict[str, Any]


@dataclass(slots=True)
class CommandBus:
    _handlers: dict[str, CommandHandler]

    def __init__(self) -> None:
        self._handlers = {}

    def register(self, command_name: str, handler: CommandHandler) -> None:
        if command_name in self._handlers:
            raise DuplicateHandlerError(f"command handler already registered: {command_name}")
        self._handlers[command_name] = handler

    async def dispatch(self, command_name: str, payload: dict[str, Any]) -> None:
        handler = self._handlers.get(command_name)
        if handler is None:
            raise UnknownHandlerError(f"unknown command handler: {command_name}")
        envelope = CommandEnvelope(name=command_name, payload=dict(payload))
        result = handler(envelope.payload)
        if isawaitable(result):
            await result


@dataclass(slots=True)
class QueryBus:
    _handlers: dict[str, QueryHandler]

    def __init__(self) -> None:
        self._handlers = {}

    def register(self, query_name: str, handler: QueryHandler) -> None:
        if query_name in self._handlers:
            raise DuplicateHandlerError(f"query handler already registered: {query_name}")
        self._handlers[query_name] = handler

    async def ask(self, query_name: str, payload: dict[str, Any]) -> Any:
        handler = self._handlers.get(query_name)
        if handler is None:
            raise UnknownHandlerError(f"unknown query handler: {query_name}")
        envelope = QueryEnvelope(name=query_name, payload=dict(payload))
        result = handler(envelope.payload)
        if isawaitable(result):
            return await result
        return result
