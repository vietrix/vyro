from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_type_hints

from vyro.jsonschema import annotation_to_schema
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
            "parameters": _build_parameters(route),
            "responses": {"200": {"description": "Successful Response"}},
            "deprecated": route.deprecated is not None,
            "x-vyro-deprecation-message": route.deprecated,
        }

    return {
        "openapi": "3.1.0",
        "info": {"title": details.title, "version": details.version},
        "paths": paths,
    }


def write_openapi_document(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _build_parameters(route: RouteRecord) -> list[dict[str, Any]]:
    signature = inspect.signature(route.handler)
    resolved_hints = get_type_hints(route.handler)
    params = list(signature.parameters.values())[1:]
    path_params = set(re.findall(r"\{[*]?([a-zA-Z_][a-zA-Z0-9_]*)\}", route.normalized_path))
    rendered: list[dict[str, Any]] = []
    for param in params:
        location = "path" if param.name in path_params else "query"
        required = location == "path" or param.default is inspect._empty
        rendered.append(
            {
                "name": param.name,
                "in": location,
                "required": required,
                "schema": annotation_to_schema(resolved_hints.get(param.name, param.annotation)),
            }
        )
    return rendered
