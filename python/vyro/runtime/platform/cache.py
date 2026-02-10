from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Protocol


class CacheBackend(Protocol):
    def get(self, key: str) -> Any | None:
        ...

    def set(self, key: str, value: Any, *, ttl_sec: float | None = None) -> None:
        ...

    def delete(self, key: str) -> None:
        ...


@dataclass(slots=True)
class MemoryCacheBackend:
    _values: dict[str, tuple[Any, float | None]] = field(default_factory=dict)

    def get(self, key: str) -> Any | None:
        if key not in self._values:
            return None
        value, expires_at = self._values[key]
        if expires_at is not None and time.time() >= expires_at:
            self._values.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, *, ttl_sec: float | None = None) -> None:
        expires_at = None if ttl_sec is None else time.time() + ttl_sec
        self._values[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._values.pop(key, None)


@dataclass(slots=True)
class RedisCacheBackend:
    client: Any
    prefix: str = "vyro:"

    def get(self, key: str) -> Any | None:
        value = self.client.get(self._k(key))
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    def set(self, key: str, value: Any, *, ttl_sec: float | None = None) -> None:
        namespaced = self._k(key)
        if ttl_sec is None:
            self.client.set(namespaced, value)
            return
        self.client.setex(namespaced, int(ttl_sec), value)

    def delete(self, key: str) -> None:
        self.client.delete(self._k(key))

    def _k(self, key: str) -> str:
        return f"{self.prefix}{key}"
