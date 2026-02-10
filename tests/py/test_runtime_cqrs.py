from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.cqrs import CommandBus, DuplicateHandlerError, QueryBus, UnknownHandlerError


def test_command_bus_dispatches_async_handler() -> None:
    bus = CommandBus()
    seen: list[int] = []

    async def on_create(payload):  # type: ignore[no-untyped-def]
        seen.append(payload["id"])

    bus.register("user.create", on_create)
    asyncio.run(bus.dispatch("user.create", {"id": 42}))
    assert seen == [42]


def test_command_bus_rejects_duplicate_handler() -> None:
    bus = CommandBus()

    def noop(payload):  # type: ignore[no-untyped-def]
        del payload

    bus.register("user.create", noop)
    with pytest.raises(DuplicateHandlerError):
        bus.register("user.create", noop)


def test_query_bus_returns_handler_result() -> None:
    bus = QueryBus()

    def on_get(payload):  # type: ignore[no-untyped-def]
        return {"id": payload["id"], "name": "vyro"}

    bus.register("user.get", on_get)
    result = asyncio.run(bus.ask("user.get", {"id": 7}))
    assert result == {"id": 7, "name": "vyro"}


def test_query_bus_raises_for_unknown_query() -> None:
    bus = QueryBus()
    with pytest.raises(UnknownHandlerError):
        asyncio.run(bus.ask("missing", {"x": 1}))
