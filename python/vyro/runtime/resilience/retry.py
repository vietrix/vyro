from __future__ import annotations

from dataclasses import dataclass, field
from random import random
from typing import Callable


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_sec: float = 0.05
    max_delay_sec: float = 1.0
    jitter_ratio: float = 0.2
    _rand: Callable[[], float] = field(default=random, repr=False)

    def next_delay(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt must be >= 1")
        exp_delay = min(self.base_delay_sec * (2 ** (attempt - 1)), self.max_delay_sec)
        jitter_span = exp_delay * self.jitter_ratio
        jitter = (self._rand() * 2.0 - 1.0) * jitter_span
        return max(0.0, min(self.max_delay_sec, exp_delay + jitter))

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_attempts
