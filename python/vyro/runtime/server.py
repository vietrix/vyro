from __future__ import annotations

import importlib
from typing import Any, Callable


def run_native_server(
    host: str,
    port: int,
    workers: int,
    routes: list[tuple[str, str, Callable[..., Any]]],
) -> None:
    native = importlib.import_module("vyro._native")
    native.start_server(host, port, max(workers, 1), routes)
