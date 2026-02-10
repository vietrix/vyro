from __future__ import annotations

import pytest

from vyro.routing.aot import compile_routes
from vyro.typing import RouteRecord


async def _dispatch_a(native_ctx: dict) -> object:
    return native_ctx


async def _dispatch_b(native_ctx: dict) -> object:
    return native_ctx


def test_compile_routes_is_deterministic() -> None:
    routes = [
        RouteRecord(
            method="POST",
            original_path="/users",
            normalized_path="/users",
            dispatch=_dispatch_a,
        ),
        RouteRecord(
            method="GET",
            original_path="/users/:id",
            normalized_path="/users/{id}",
            dispatch=_dispatch_b,
        ),
    ]

    compiled = compile_routes(routes)
    assert compiled[0][0] == "GET"
    assert compiled[0][1] == "/users/{id}"
    assert compiled[1][0] == "POST"
    assert compiled[1][1] == "/users"


def test_compile_routes_rejects_duplicates() -> None:
    routes = [
        RouteRecord(
            method="GET",
            original_path="/users/:id",
            normalized_path="/users/{id}",
            dispatch=_dispatch_a,
        ),
        RouteRecord(
            method="GET",
            original_path="/users/:uid",
            normalized_path="/users/{id}",
            dispatch=_dispatch_b,
        ),
    ]

    with pytest.raises(ValueError, match="Duplicate route declaration detected"):
        compile_routes(routes)
