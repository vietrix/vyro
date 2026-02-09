from __future__ import annotations

from vyro.settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKERS


def defaults() -> tuple[str, int, int]:
    return DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKERS
