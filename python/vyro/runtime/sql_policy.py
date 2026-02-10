from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable

from .sql import AsyncSQLAdapter


SlowQueryHook = Callable[[str, float], None]


@dataclass(slots=True)
class QueryExecutionPolicy:
    timeout_sec: float = 5.0
    slow_query_threshold_ms: float = 200.0
    on_slow_query: SlowQueryHook | None = None

    def set_slow_query_hook(self, hook: SlowQueryHook | None) -> None:
        self.on_slow_query = hook


@dataclass(slots=True)
class PolicySQLAdapter:
    inner: AsyncSQLAdapter
    policy: QueryExecutionPolicy

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        started = perf_counter()
        result = await asyncio.wait_for(
            self.inner.execute(query, params),
            timeout=self.policy.timeout_sec,
        )
        self._maybe_report_slow(query, started)
        return result

    async def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        started = perf_counter()
        result = await asyncio.wait_for(
            self.inner.fetch_all(query, params),
            timeout=self.policy.timeout_sec,
        )
        self._maybe_report_slow(query, started)
        return result

    def _maybe_report_slow(self, query: str, started: float) -> None:
        elapsed_ms = (perf_counter() - started) * 1000.0
        hook = self.policy.on_slow_query
        if hook is not None and elapsed_ms >= self.policy.slow_query_threshold_ms:
            hook(query, elapsed_ms)
