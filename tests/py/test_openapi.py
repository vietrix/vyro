from __future__ import annotations

import json
from pathlib import Path

from vyro.openapi import OpenAPIMeta, build_openapi_document, write_openapi_document
from vyro.typing import RouteRecord


async def _dispatch(native_ctx: dict) -> object:
    return native_ctx


def test_build_openapi_document_from_routes() -> None:
    routes = [
        RouteRecord(
            method="GET",
            original_path="/users/:id",
            normalized_path="/users/{id}",
            dispatch=_dispatch,
        )
    ]
    doc = build_openapi_document(routes, OpenAPIMeta(title="Demo", version="1.2.3"))
    assert doc["openapi"] == "3.1.0"
    assert doc["info"]["title"] == "Demo"
    assert "/users/{id}" in doc["paths"]
    assert "get" in doc["paths"]["/users/{id}"]


def test_write_openapi_document(tmp_path: Path) -> None:
    out = tmp_path / "openapi.json"
    write_openapi_document(
        out,
        {
            "openapi": "3.1.0",
            "info": {"title": "Demo", "version": "1.0.0"},
            "paths": {},
        },
    )
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["info"]["title"] == "Demo"
