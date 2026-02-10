from __future__ import annotations

import pytest

from vyro.errors import HandlerSignatureError, RouteDefinitionError
from vyro.runtime.websocket import WebSocketRouteRegistry


def test_websocket_registry_accepts_async_handler_and_normalizes_path() -> None:
    registry = WebSocketRouteRegistry()

    async def ws_handler(ctx):  # type: ignore[no-untyped-def]
        return ctx

    normalized = registry.add("/ws/:room", ws_handler)
    assert normalized == "/ws/{room}"
    assert registry.get("/ws/:room") is ws_handler


def test_websocket_registry_rejects_sync_handler() -> None:
    registry = WebSocketRouteRegistry()

    def ws_handler(ctx):  # type: ignore[no-untyped-def]
        return ctx

    with pytest.raises(HandlerSignatureError, match="async def"):
        registry.add("/ws", ws_handler)  # type: ignore[arg-type]


def test_websocket_registry_rejects_duplicate_path() -> None:
    registry = WebSocketRouteRegistry()

    async def first(ctx):  # type: ignore[no-untyped-def]
        return ctx

    async def second(ctx):  # type: ignore[no-untyped-def]
        return ctx

    registry.add("/ws/:room", first)
    with pytest.raises(RouteDefinitionError, match="duplicate websocket route"):
        registry.add("/ws/:room", second)
