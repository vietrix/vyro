from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RouteConcurrencyLimiter:
    default_limit: int = 256
    _limits: dict[str, int] = field(default_factory=dict)
    _inflight: dict[str, int] = field(default_factory=dict)

    def set_limit(self, route: str, limit: int) -> None:
        self._limits[route] = max(1, limit)

    def acquire(self, route: str) -> bool:
        limit = self._limits.get(route, self.default_limit)
        current = self._inflight.get(route, 0)
        if current >= limit:
            return False
        self._inflight[route] = current + 1
        return True

    def release(self, route: str) -> None:
        current = self._inflight.get(route, 0)
        if current <= 1:
            self._inflight.pop(route, None)
            return
        self._inflight[route] = current - 1

    def inflight(self, route: str) -> int:
        return self._inflight.get(route, 0)
