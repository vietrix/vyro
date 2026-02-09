from __future__ import annotations

from typing import Any

from .base import Middleware


class MiddlewareChain:
    def __init__(self, middlewares: list[Middleware] | None = None) -> None:
        self._middlewares = list(middlewares or [])

    async def run_before(self, ctx: Any) -> None:
        for mw in self._middlewares:
            await mw.before_request(ctx)

    async def run_after(self, ctx: Any, response: Any) -> Any:
        current = response
        for mw in reversed(self._middlewares):
            current = await mw.after_response(ctx, current)
        return current
