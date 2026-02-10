from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.sql_policy import PolicySQLAdapter, QueryExecutionPolicy


class FakeAdapter:
    def __init__(self, delay_sec: float = 0.0) -> None:
        self.delay_sec = delay_sec

    async def execute(self, query, params=()):  # type: ignore[no-untyped-def]
        await asyncio.sleep(self.delay_sec)
        return 1

    async def fetch_all(self, query, params=()):  # type: ignore[no-untyped-def]
        await asyncio.sleep(self.delay_sec)
        return [{"ok": True}]


def test_policy_sql_adapter_enforces_timeout() -> None:
    adapter = PolicySQLAdapter(
        inner=FakeAdapter(delay_sec=0.05),
        policy=QueryExecutionPolicy(timeout_sec=0.01),
    )
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(adapter.execute("SELECT 1"))


def test_policy_sql_adapter_reports_slow_query() -> None:
    seen: list[tuple[str, float]] = []
    policy = QueryExecutionPolicy(timeout_sec=1.0, slow_query_threshold_ms=0.0)
    policy.set_slow_query_hook(lambda query, elapsed: seen.append((query, elapsed)))
    adapter = PolicySQLAdapter(inner=FakeAdapter(delay_sec=0.0), policy=policy)
    rows = asyncio.run(adapter.fetch_all("SELECT 1"))
    assert rows == [{"ok": True}]
    assert seen
    assert seen[0][0] == "SELECT 1"
