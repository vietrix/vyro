from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class TokenBucketRateLimiter:
    rate_per_sec: float
    burst: int
    _tokens: float = 0.0
    _last_refill: float = 0.0

    def __post_init__(self) -> None:
        self._tokens = float(max(1, self.burst))
        self._last_refill = monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        self._refill()
        if self._tokens < cost:
            return False
        self._tokens -= cost
        return True

    def _refill(self) -> None:
        now = monotonic()
        elapsed = max(0.0, now - self._last_refill)
        self._last_refill = now
        self._tokens = min(float(max(1, self.burst)), self._tokens + elapsed * self.rate_per_sec)

    @property
    def tokens(self) -> float:
        return self._tokens
