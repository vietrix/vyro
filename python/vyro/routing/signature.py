from __future__ import annotations

import inspect
from typing import Any

from vyro.errors import HandlerSignatureError


def convert_path_value(value: str, annotation: Any) -> Any:
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


def bind_path_kwargs(
    handler_name: str,
    params: list[inspect.Parameter],
    path_params: dict[str, str],
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    for param in params[1:]:
        if param.name not in path_params:
            if param.default is inspect._empty:
                raise HandlerSignatureError(
                    f"Missing path parameter '{param.name}' for handler '{handler_name}'"
                )
            continue
        kwargs[param.name] = convert_path_value(path_params[param.name], param.annotation)
    return kwargs
