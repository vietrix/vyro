from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProbeState:
    live: bool = True
    ready: bool = False
    started: bool = False


class HealthProbes:
    def __init__(self) -> None:
        self._state = ProbeState()

    def mark_started(self) -> None:
        self._state.started = True

    def mark_ready(self) -> None:
        self._state.ready = True

    def mark_not_ready(self) -> None:
        self._state.ready = False

    def mark_unhealthy(self) -> None:
        self._state.live = False

    def mark_healthy(self) -> None:
        self._state.live = True

    def liveness(self) -> dict[str, Any]:
        return {"status": "ok" if self._state.live else "fail", "live": self._state.live}

    def readiness(self) -> dict[str, Any]:
        return {"status": "ok" if self._state.ready else "fail", "ready": self._state.ready}

    def startup(self) -> dict[str, Any]:
        return {"status": "ok" if self._state.started else "fail", "started": self._state.started}
