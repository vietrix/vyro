from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from ..errors import HandlerSignatureError, RouteDefinitionError
from ..routing.normalize import normalize_path

WebSocketHandler = Callable[..., Awaitable[Any]]


@dataclass(slots=True)
class WebSocketRouteRegistry:
    _routes: dict[str, WebSocketHandler] = field(default_factory=dict)

    def add(self, path: str, handler: WebSocketHandler) -> str:
        normalized = normalize_path(path)
        if not inspect.iscoroutinefunction(handler):
            raise HandlerSignatureError("websocket handler must be declared with async def")
        if normalized in self._routes:
            raise RouteDefinitionError(f"duplicate websocket route: {normalized}")
        self._routes[normalized] = handler
        return normalized

    def get(self, path: str) -> WebSocketHandler | None:
        normalized = normalize_path(path)
        return self._routes.get(normalized)

    def routes(self) -> dict[str, WebSocketHandler]:
        return dict(self._routes)
