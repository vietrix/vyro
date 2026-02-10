from __future__ import annotations

from typing import Any


class Middleware:
    priority: int = 100

    async def before_request(self, ctx: Any) -> None:
        return None

    async def after_response(self, ctx: Any, response: Any) -> Any:
        return response
