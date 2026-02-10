from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vyro.typing import RouteRecord


@dataclass(slots=True)
class OpenAPIMeta:
    title: str = "Vyro API"
    version: str = "0.1.0"


def build_openapi_document(routes: list[RouteRecord], meta: OpenAPIMeta | None = None) -> dict[str, Any]:
    details = meta or OpenAPIMeta()
    paths: dict[str, dict[str, Any]] = {}
    for route in routes:
        path = route.normalized_path
        method = route.method.lower()
        operation_id = f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '') or 'root'}"
        paths.setdefault(path, {})[method] = {
            "operationId": operation_id,
            "responses": {"200": {"description": "Successful Response"}},
        }

    return {
        "openapi": "3.1.0",
        "info": {"title": details.title, "version": details.version},
        "paths": paths,
    }


def write_openapi_document(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
