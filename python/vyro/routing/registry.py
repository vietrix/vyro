from __future__ import annotations

from typing import Any, Callable

from vyro.routing.dispatch import build_dispatch
from vyro.routing.normalize import normalize_path
from vyro.routing.validate import validate_handler
from vyro.typing import RouteRecord


class RouterRegistry:
    def __init__(self) -> None:
        self._routes: list[RouteRecord] = []

    def add_route(self, method: str, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        normalized_path = normalize_path(path)
        upper_method = method.upper()

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            params = validate_handler(fn)
            dispatch = build_dispatch(fn, params)
            self._routes.append(
                RouteRecord(
                    method=upper_method,
                    original_path=path,
                    normalized_path=normalized_path,
                    dispatch=dispatch,
                )
            )
            return fn

        return decorator

    def export_native(self) -> list[tuple[str, str, Callable[..., Any]]]:
        return [(route.method, route.normalized_path, route.dispatch) for route in self._routes]
