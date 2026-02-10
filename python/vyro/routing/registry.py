from __future__ import annotations

from typing import Any, Callable

from vyro.routing.aot import compile_routes
from vyro.routing.dispatch import build_dispatch
from vyro.routing.normalize import normalize_path
from vyro.routing.validate import validate_handler
from vyro.typing import NativeRoute, RouteRecord


class RouterRegistry:
    def __init__(self) -> None:
        self._routes: list[RouteRecord] = []
        self._compiled: list[NativeRoute] | None = None

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
            self._compiled = None
            return fn

        return decorator

    def compile(self) -> list[NativeRoute]:
        if self._compiled is None:
            self._compiled = compile_routes(self._routes)
        return list(self._compiled)

    def export_native(self) -> list[NativeRoute]:
        return self.compile()
