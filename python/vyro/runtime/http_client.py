from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen

from .timeout_budget import TimeoutBudget


@dataclass(slots=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes

    def text(self, encoding: str = "utf-8") -> str:
        return self.body.decode(encoding)

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class AsyncHttpClient:
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout_sec: float | None = None,
        budget: TimeoutBudget | None = None,
    ) -> HttpResponse:
        effective_timeout = timeout_sec
        if budget is not None:
            budget_timeout = budget.remaining_sec
            if effective_timeout is None:
                effective_timeout = budget_timeout
            else:
                effective_timeout = min(effective_timeout, budget_timeout)
        if effective_timeout is not None and effective_timeout <= 0:
            raise TimeoutError("timeout budget expired")

        request = Request(url=url, data=body, method=method.upper(), headers=headers or {})
        return await asyncio.to_thread(self._send, request, effective_timeout)

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout_sec: float | None = None,
        budget: TimeoutBudget | None = None,
    ) -> HttpResponse:
        return await self.request(
            "GET",
            url,
            headers=headers,
            timeout_sec=timeout_sec,
            budget=budget,
        )

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout_sec: float | None = None,
        budget: TimeoutBudget | None = None,
    ) -> HttpResponse:
        return await self.request(
            "POST",
            url,
            headers=headers,
            body=body,
            timeout_sec=timeout_sec,
            budget=budget,
        )

    @staticmethod
    def _send(request: Request, timeout_sec: float | None) -> HttpResponse:
        with urlopen(request, timeout=timeout_sec) as raw:  # noqa: S310
            status = getattr(raw, "status", 200)
            headers = {k: v for k, v in raw.headers.items()}
            body = raw.read()
            return HttpResponse(status=status, headers=headers, body=body)
