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

    def add_route(
        self,
        method: str,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        normalized_path = normalize_path(path)
        version_prefix = _normalize_version(version) if version is not None else None
        routed_path = f"{version_prefix}{normalized_path}" if version_prefix else normalized_path
        upper_method = method.upper()

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            params = validate_handler(fn)
            dispatch = build_dispatch(fn, params)
            self._routes.append(
                RouteRecord(
                    method=upper_method,
                    original_path=path,
                    normalized_path=routed_path,
                    dispatch=dispatch,
                    handler=fn,
                    version=version_prefix,
                    deprecated=_normalize_deprecation(deprecated),
                )
            )
            self._compiled = None
            return fn

        return decorator

    def compile(self) -> list[NativeRoute]:
        if self._compiled is None:
            self._compiled = compile_routes(self._routes)
        return list(self._compiled)

    def records(self) -> list[RouteRecord]:
        return list(self._routes)

    def export_native(self) -> list[NativeRoute]:
        return self.compile()


def _normalize_version(version: str) -> str:
    value = version.strip().lower()
    if not value:
        raise ValueError("version cannot be empty")
    if value.startswith("v"):
        return f"/{value}"
    return f"/v{value}"


def _normalize_deprecation(value: bool | str) -> str | None:
    if value is False:
        return None
    if value is True:
        return "deprecated"
    cleaned = value.strip()
    if not cleaned:
        return "deprecated"
    return cleaned
