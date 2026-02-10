from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256


Color = str


@dataclass(frozen=True, slots=True)
class BlueGreenState:
    active_color: Color = "blue"
    traffic_to_green_percent: int = 0
    pinned_actors: dict[str, Color] = field(default_factory=dict)


@dataclass(slots=True)
class BlueGreenRolloutHelper:
    _state: BlueGreenState = field(default_factory=BlueGreenState)

    @property
    def state(self) -> BlueGreenState:
        return self._state

    def promote(self, color: Color) -> None:
        self._state = BlueGreenState(
            active_color=color,
            traffic_to_green_percent=100 if color == "green" else 0,
            pinned_actors=dict(self._state.pinned_actors),
        )

    def set_traffic_to_green(self, percent: int) -> None:
        bounded = max(0, min(100, percent))
        self._state = BlueGreenState(
            active_color=self._state.active_color,
            traffic_to_green_percent=bounded,
            pinned_actors=dict(self._state.pinned_actors),
        )

    def pin_actor(self, actor_id: str, color: Color) -> None:
        pins = dict(self._state.pinned_actors)
        pins[actor_id] = color
        self._state = BlueGreenState(
            active_color=self._state.active_color,
            traffic_to_green_percent=self._state.traffic_to_green_percent,
            pinned_actors=pins,
        )

    def unpin_actor(self, actor_id: str) -> None:
        if actor_id not in self._state.pinned_actors:
            return
        pins = dict(self._state.pinned_actors)
        del pins[actor_id]
        self._state = BlueGreenState(
            active_color=self._state.active_color,
            traffic_to_green_percent=self._state.traffic_to_green_percent,
            pinned_actors=pins,
        )

    def select_color(self, actor_id: str | None = None) -> Color:
        if actor_id is not None:
            pinned = self._state.pinned_actors.get(actor_id)
            if pinned is not None:
                return pinned
        percent = self._state.traffic_to_green_percent
        if percent <= 0:
            return "blue"
        if percent >= 100:
            return "green"
        subject = actor_id or ""
        bucket = _stable_bucket(subject)
        return "green" if bucket < percent else "blue"


def _stable_bucket(value: str) -> int:
    digest = sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100
