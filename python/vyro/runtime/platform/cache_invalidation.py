from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .cache import CacheBackend


InvalidationHook = Callable[[str], None]


@dataclass(slots=True)
class CacheInvalidationHooks:
    _on_set: list[InvalidationHook] = field(default_factory=list)
    _on_delete: list[InvalidationHook] = field(default_factory=list)

    def on_set(self, hook: InvalidationHook) -> None:
        self._on_set.append(hook)

    def on_delete(self, hook: InvalidationHook) -> None:
        self._on_delete.append(hook)

    def set(
        self,
        backend: CacheBackend,
        key: str,
        value: Any,
        *,
        ttl_sec: float | None = None,
    ) -> None:
        backend.set(key, value, ttl_sec=ttl_sec)
        for hook in self._on_set:
            hook(key)

    def delete(self, backend: CacheBackend, key: str) -> None:
        backend.delete(key)
        for hook in self._on_delete:
            hook(key)
