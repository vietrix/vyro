from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .base import Middleware


class MiddlewareChain:
    def __init__(self, middlewares: list[Middleware] | None = None) -> None:
        self._middlewares = list(middlewares or [])
        self._before_hooks, self._after_hooks = self._compile_hooks(self._middlewares)

    async def run_before(self, ctx: Any) -> None:
        for hook in self._before_hooks:
            await hook(ctx)

    async def run_after(self, ctx: Any, response: Any) -> Any:
        current = response
        for hook in self._after_hooks:
            current = await hook(ctx, current)
        return current

    @staticmethod
    def _compile_hooks(
        middlewares: list[Middleware],
    ) -> tuple[list[Callable[[Any], Awaitable[Any]]], list[Callable[[Any, Any], Awaitable[Any]]]]:
        before_hooks: list[Callable[[Any], Awaitable[Any]]] = []
        after_hooks: list[Callable[[Any, Any], Awaitable[Any]]] = []
        for mw in middlewares:
            if not _is_default_before(mw):
                before_hooks.append(mw.before_request)
            if not _is_default_after(mw):
                after_hooks.append(mw.after_response)
        return before_hooks, list(reversed(after_hooks))


def _is_default_before(mw: Middleware) -> bool:
    cls_impl = mw.__class__.__dict__.get("before_request")
    return cls_impl is None or cls_impl is Middleware.before_request


def _is_default_after(mw: Middleware) -> bool:
    cls_impl = mw.__class__.__dict__.get("after_response")
    return cls_impl is None or cls_impl is Middleware.after_response
