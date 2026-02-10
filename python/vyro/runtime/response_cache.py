from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .cache import CacheBackend, MemoryCacheBackend


@dataclass(slots=True)
class ResponseCachePolicy:
    default_ttl_sec: float = 30.0
    _route_ttl: dict[tuple[str, str], float] = field(default_factory=dict)

    def set_ttl(self, *, method: str, route: str, ttl_sec: float) -> None:
        self._route_ttl[(method.upper(), route)] = ttl_sec

    def ttl_for(self, *, method: str, route: str) -> float:
        return self._route_ttl.get((method.upper(), route), self.default_ttl_sec)


@dataclass(slots=True)
class ResponseCacheService:
    backend: CacheBackend = field(default_factory=MemoryCacheBackend)
    policy: ResponseCachePolicy = field(default_factory=ResponseCachePolicy)

    def make_key(self, *, method: str, path: str, query: str = "") -> str:
        suffix = f"?{query}" if query else ""
        return f"resp:{method.upper()}:{path}{suffix}"

    def get(self, *, method: str, path: str, query: str = "") -> Any | None:
        return self.backend.get(self.make_key(method=method, path=path, query=query))

    def set(
        self,
        *,
        method: str,
        path: str,
        response: Any,
        query: str = "",
    ) -> None:
        key = self.make_key(method=method, path=path, query=query)
        ttl = self.policy.ttl_for(method=method, route=path)
        self.backend.set(key, response, ttl_sec=ttl)
