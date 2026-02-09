from __future__ import annotations

import inspect
from typing import Any, Callable

from vyro.http.context import Context
from vyro.routing.signature import bind_path_kwargs


def build_dispatch(
    fn: Callable[..., Any],
    params: list[inspect.Parameter],
) -> Callable[[dict[str, Any]], Any]:
    async def dispatch(native_ctx: dict[str, Any]) -> Any:
        ctx = Context.from_native(native_ctx)
        kwargs = bind_path_kwargs(fn.__name__, params, dict(ctx.path_params))
        return await fn(ctx, **kwargs)

    return dispatch
