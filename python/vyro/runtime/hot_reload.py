from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class RuntimeConfigReloadError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RuntimeConfigSnapshot:
    values: dict[str, Any]
    version: int = 1

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass(slots=True)
class SafeRuntimeConfigReloader:
    allowed_keys: frozenset[str] = field(default_factory=lambda: frozenset({"workers", "log_level", "rate_limit"}))
    _current: RuntimeConfigSnapshot = field(default_factory=lambda: RuntimeConfigSnapshot(values={}))
    _previous: RuntimeConfigSnapshot | None = None

    @property
    def current(self) -> RuntimeConfigSnapshot:
        return self._current

    @property
    def previous(self) -> RuntimeConfigSnapshot | None:
        return self._previous

    def load_initial(self, values: dict[str, Any]) -> RuntimeConfigSnapshot:
        self._validate(values)
        snapshot = RuntimeConfigSnapshot(values=dict(values), version=1)
        self._current = snapshot
        self._previous = None
        return snapshot

    def apply(self, patch: dict[str, Any]) -> RuntimeConfigSnapshot:
        self._validate(patch)
        merged = dict(self._current.values)
        merged.update(patch)
        next_snapshot = RuntimeConfigSnapshot(values=merged, version=self._current.version + 1)
        self._previous = self._current
        self._current = next_snapshot
        return next_snapshot

    def rollback(self) -> RuntimeConfigSnapshot:
        if self._previous is None:
            raise RuntimeConfigReloadError("no previous runtime config snapshot available")
        self._current, self._previous = self._previous, None
        return self._current

    def _validate(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if key not in self.allowed_keys:
                raise RuntimeConfigReloadError(f"runtime config key is not hot-reloadable: {key}")
            if key == "workers" and (not isinstance(value, int) or value < 1):
                raise RuntimeConfigReloadError("workers must be an integer >= 1")
            if key == "log_level" and value not in {"debug", "info", "warn", "error"}:
                raise RuntimeConfigReloadError("log_level must be one of: debug, info, warn, error")
            if key == "rate_limit" and (not isinstance(value, int) or value < 1):
                raise RuntimeConfigReloadError("rate_limit must be an integer >= 1")
