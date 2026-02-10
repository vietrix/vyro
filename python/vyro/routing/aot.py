from __future__ import annotations

from vyro.typing import NativeRoute, RouteRecord


def compile_routes(routes: list[RouteRecord]) -> list[NativeRoute]:
    """Compile declared routes into a deterministic native plan."""
    seen: set[tuple[str, str]] = set()
    compiled: list[NativeRoute] = []
    for route in sorted(routes, key=lambda item: (item.method, item.normalized_path)):
        key = (route.method, route.normalized_path)
        if key in seen:
            raise ValueError(f"Duplicate route declaration detected for {route.method} {route.original_path}")
        seen.add(key)
        compiled.append((route.method, route.normalized_path, route.dispatch))
    return compiled
