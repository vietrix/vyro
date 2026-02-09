from __future__ import annotations

import inspect
from typing import Any, Callable

from vyro.errors import HandlerSignatureError


def validate_handler(fn: Callable[..., Any]) -> list[inspect.Parameter]:
    if not inspect.iscoroutinefunction(fn):
        raise HandlerSignatureError(f"Handler '{fn.__name__}' must be declared with async def.")

    params = list(inspect.signature(fn).parameters.values())
    if not params:
        raise HandlerSignatureError(f"Handler '{fn.__name__}' must accept first argument 'ctx'.")
    return params
