from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import inspect
from typing import Any, get_args, get_origin
from uuid import UUID


TYPE_MAP: dict[type[Any], dict[str, Any]] = {
    str: {"type": "string"},
    int: {"type": "integer"},
    float: {"type": "number"},
    bool: {"type": "boolean"},
    UUID: {"type": "string", "format": "uuid"},
    datetime: {"type": "string", "format": "date-time"},
    date: {"type": "string", "format": "date"},
    Decimal: {"type": "string", "format": "decimal"},
}


def annotation_to_schema(annotation: Any) -> dict[str, Any]:
    if annotation is inspect._empty:
        return {"type": "string"}

    origin = get_origin(annotation)
    if origin is not None:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]  # noqa: E721
        if len(args) == 1:
            return annotation_to_schema(args[0])

    if annotation in TYPE_MAP:
        return dict(TYPE_MAP[annotation])
    return {"type": "string"}
