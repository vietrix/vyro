from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(slots=True, frozen=True)
class GracefulShutdownPolicy:
    timeout_seconds: float = 30.0
    drain_inflight: bool = True

    def deadline(self, started_at: datetime | None = None) -> datetime:
        base = started_at or datetime.now(timezone.utc)
        return base + timedelta(seconds=max(0.0, self.timeout_seconds))

    def has_timed_out(self, started_at: datetime, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return current >= self.deadline(started_at)
