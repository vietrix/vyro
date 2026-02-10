from __future__ import annotations

from .base import Middleware


class MiddlewareRegistry:
    def __init__(self) -> None:
        self._items: list[tuple[int, int, str | None, Middleware]] = []
        self._seq = 0

    def add(
        self,
        mw: Middleware,
        *,
        priority: int | None = None,
        group: str | None = None,
    ) -> None:
        value = _resolve_priority(mw, priority)
        self._items.append((value, self._seq, _normalize_group(group), mw))
        self._seq += 1

    def items(self) -> list[Middleware]:
        return [mw for _, _, _, mw in _ordered_items(self._items)]

    def items_for_path(self, path: str) -> list[Middleware]:
        selected: list[Middleware] = []
        for _, _, group, mw in _ordered_items(self._items):
            if group is None or path.startswith(group):
                selected.append(mw)
        return selected


def _resolve_priority(mw: Middleware, explicit: int | None) -> int:
    if explicit is not None:
        return explicit
    return getattr(mw, "priority", 100)


def _normalize_group(group: str | None) -> str | None:
    if group is None:
        return None
    value = group.strip()
    if not value:
        return None
    if not value.startswith("/"):
        value = f"/{value}"
    return value.rstrip("/") or "/"


def _ordered_items(
    items: list[tuple[int, int, str | None, Middleware]],
) -> list[tuple[int, int, str | None, Middleware]]:
    return sorted(items, key=lambda item: (item[0], item[1]))
