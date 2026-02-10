from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


Handler = Callable[[dict], Awaitable[object]]
NativeRoute = tuple[str, str, Handler]


@dataclass(slots=True)
class RouteRecord:
    method: str
    original_path: str
    normalized_path: str
    dispatch: Handler
    handler: Callable[..., Any]
    version: str | None = None
