from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import Middleware


@dataclass(slots=True)
class IdempotencyStore:
    _values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any | None:
        return self._values.get(key)

    def set(self, key: str, response: Any) -> None:
        self._values[key] = response


@dataclass(slots=True)
class IdempotencyKeyMiddleware(Middleware):
    header_name: str = "idempotency-key"
    store: IdempotencyStore = field(default_factory=IdempotencyStore)

    async def before_request(self, ctx: Any) -> None:
        key = self._key_from_ctx(ctx)
        if not key:
            return
        cached = self.store.get(key)
        if cached is None:
            return
        ctx.set_extension("idempotency_replay", True)
        ctx.set_extension("idempotency_response", cached)

    async def after_response(self, ctx: Any, response: Any) -> Any:
        key = self._key_from_ctx(ctx)
        if not key:
            return response

        replay = bool(ctx.get_extension("idempotency_replay", False))
        if replay:
            cached = ctx.get_extension("idempotency_response")
            if cached is not None:
                return cached
            return response

        self.store.set(key, response)
        return response

    def _key_from_ctx(self, ctx: Any) -> str | None:
        headers = getattr(ctx, "headers", {})
        return headers.get(self.header_name)
