from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Callable


@dataclass(slots=True)
class TimeoutBudget:
    timeout_sec: float
    _clock: Callable[[], float] = field(default=monotonic, repr=False)
    _started_at: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.timeout_sec <= 0:
            raise ValueError("timeout_sec must be > 0")
        self._started_at = self._clock()

    @property
    def deadline(self) -> float:
        return self._started_at + self.timeout_sec

    @property
    def remaining_sec(self) -> float:
        return max(0.0, self.deadline - self._clock())

    def is_expired(self) -> bool:
        return self.remaining_sec <= 0.0

    def child(self, timeout_sec: float | None = None) -> TimeoutBudget:
        if timeout_sec is None:
            timeout_sec = self.remaining_sec
        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be > 0")
        propagated_timeout = min(timeout_sec, self.remaining_sec)
        return TimeoutBudget(timeout_sec=propagated_timeout, _clock=self._clock)
