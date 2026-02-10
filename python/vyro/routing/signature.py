from __future__ import annotations

import inspect
from typing import Any

from vyro.errors import HandlerSignatureError


def convert_request_value(value: str, annotation: Any) -> Any:
    if annotation is inspect._empty or annotation is str:
        return value
    if annotation is int:
        return int(value)
    if annotation is float:
        return float(value)
    if annotation is bool:
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        raise ValueError(f"Cannot parse bool from '{value}'")
    return value


def bind_request_kwargs(
    handler_name: str,
    params: list[inspect.Parameter],
    path_params: dict[str, str],
    query_params: dict[str, str],
    headers: dict[str, str],
) -> dict[str, Any]:
    normalized_headers = {k.lower(): v for k, v in headers.items()}
    kwargs: dict[str, Any] = {}
    for param in params[1:]:
        raw_value: str | None = None

        if param.name in path_params:
            raw_value = path_params[param.name]
        elif param.name in query_params:
            raw_value = query_params[param.name]
        else:
            header_key = param.name.replace("_", "-").lower()
            raw_value = normalized_headers.get(header_key)

        if raw_value is None:
            if param.default is inspect._empty:
                raise HandlerSignatureError(
                    f"Missing request parameter '{param.name}' for handler '{handler_name}'"
                )
            continue

        kwargs[param.name] = convert_request_value(raw_value, param.annotation)
    return kwargs
