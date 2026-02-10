from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BackpressureController:
    max_inflight: int = 1024
    _inflight: int = 0

    def should_reject(self) -> bool:
        return self._inflight >= max(1, self.max_inflight)

    def acquire(self) -> bool:
        if self.should_reject():
            return False
        self._inflight += 1
        return True

    def release(self) -> None:
        if self._inflight > 0:
            self._inflight -= 1

    @property
    def inflight(self) -> int:
        return self._inflight
