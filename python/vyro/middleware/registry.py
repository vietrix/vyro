from __future__ import annotations

from .base import Middleware


class MiddlewareRegistry:
    def __init__(self) -> None:
        self._items: list[Middleware] = []

    def add(self, mw: Middleware) -> None:
        self._items.append(mw)

    def items(self) -> list[Middleware]:
        return list(self._items)
