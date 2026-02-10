from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class OutboundBulkhead:
    default_limit: int = 32
    _inflight: dict[str, int] = field(default_factory=dict)
    _limits: dict[str, int] = field(default_factory=dict)

    def set_limit(self, dependency: str, limit: int) -> None:
        if limit <= 0:
            raise ValueError("limit must be > 0")
        self._limits[dependency] = limit

    def acquire(self, dependency: str) -> bool:
        limit = self._limits.get(dependency, self.default_limit)
        if self.inflight(dependency) >= limit:
            return False
        self._inflight[dependency] = self.inflight(dependency) + 1
        return True

    def release(self, dependency: str) -> None:
        current = self.inflight(dependency)
        if current <= 1:
            self._inflight.pop(dependency, None)
            return
        self._inflight[dependency] = current - 1

    def inflight(self, dependency: str) -> int:
        return self._inflight.get(dependency, 0)
