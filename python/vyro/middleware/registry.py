from __future__ import annotations

from .base import Middleware


class MiddlewareRegistry:
    def __init__(self) -> None:
        self._items: list[tuple[int, int, Middleware]] = []
        self._seq = 0

    def add(self, mw: Middleware, *, priority: int | None = None) -> None:
        value = _resolve_priority(mw, priority)
        self._items.append((value, self._seq, mw))
        self._seq += 1

    def items(self) -> list[Middleware]:
        ordered = sorted(self._items, key=lambda item: (item[0], item[1]))
        return [mw for _, _, mw in ordered]


def _resolve_priority(mw: Middleware, explicit: int | None) -> int:
    if explicit is not None:
        return explicit
    return getattr(mw, "priority", 100)
