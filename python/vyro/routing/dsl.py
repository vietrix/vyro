from __future__ import annotations

from vyro.routing.normalize import normalize_path


def to_native_pattern(path: str) -> str:
    return normalize_path(path)
