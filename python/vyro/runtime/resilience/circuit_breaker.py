from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Callable


@dataclass(slots=True)
class OutboundCircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout_sec: float = 10.0
    half_open_max_calls: int = 1
    _state: str = "closed"
    _failures: int = 0
    _opened_at: float | None = None
    _half_open_calls: int = 0
    _clock: Callable[[], float] = field(default=monotonic, repr=False)

    @property
    def state(self) -> str:
        self._refresh_state()
        return self._state

    def allow_request(self) -> bool:
        self._refresh_state()
        if self._state == "open":
            return False
        if self._state == "half-open":
            if self._half_open_calls >= self.half_open_max_calls:
                return False
            self._half_open_calls += 1
        return True

    def record_success(self) -> None:
        self._state = "closed"
        self._failures = 0
        self._opened_at = None
        self._half_open_calls = 0

    def record_failure(self) -> None:
        self._refresh_state()
        if self._state == "half-open":
            self._trip_open()
            return
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._trip_open()

    def _trip_open(self) -> None:
        self._state = "open"
        self._opened_at = self._clock()
        self._half_open_calls = 0

    def _refresh_state(self) -> None:
        if self._state != "open" or self._opened_at is None:
            return
        if self._clock() - self._opened_at >= self.recovery_timeout_sec:
            self._state = "half-open"
            self._half_open_calls = 0
