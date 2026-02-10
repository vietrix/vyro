from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from vyro.openapi import OpenAPIMeta, build_openapi_document, write_openapi_document
from vyro.typing import RouteRecord


async def _dispatch(native_ctx: dict) -> object:
    return native_ctx


async def _handler(ctx, id: int, trace_id: UUID):  # type: ignore[no-untyped-def]
    return {"id": id, "trace_id": str(trace_id)}


def test_build_openapi_document_from_routes() -> None:
    routes = [
        RouteRecord(
            method="GET",
            original_path="/users/:id",
            normalized_path="/users/{id}",
            dispatch=_dispatch,
            handler=_handler,
        ),
        RouteRecord(
            method="GET",
            original_path="/legacy",
            normalized_path="/legacy",
            dispatch=_dispatch,
            handler=_handler,
            deprecated="use /v2/users/{id}",
        ),
    ]
    doc = build_openapi_document(routes, OpenAPIMeta(title="Demo", version="1.2.3"))
    assert doc["openapi"] == "3.1.0"
    assert doc["info"]["title"] == "Demo"
    assert "/users/{id}" in doc["paths"]
    assert "get" in doc["paths"]["/users/{id}"]
    params = doc["paths"]["/users/{id}"]["get"]["parameters"]
    assert params[0]["in"] == "path"
    assert params[0]["schema"]["type"] == "integer"
    assert params[1]["in"] == "query"
    assert params[1]["schema"]["format"] == "uuid"
    assert doc["paths"]["/users/{id}"]["get"]["deprecated"] is False
    assert doc["paths"]["/legacy"]["get"]["deprecated"] is True
    assert doc["paths"]["/legacy"]["get"]["x-vyro-deprecation-message"] == "use /v2/users/{id}"


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
