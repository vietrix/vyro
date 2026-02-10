from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.cron import CronScheduler


def test_cron_scheduler_runs_due_jobs() -> None:
    scheduler = CronScheduler()
    calls: list[str] = []

    async def task() -> None:
        calls.append("ran")

    async def run() -> None:
        scheduler.add_job(name="heartbeat", interval_sec=0.01, handler=task)
        ran = await scheduler.run_pending()
        assert ran == 1

    asyncio.run(run())
    assert calls == ["ran"]


def test_cron_scheduler_validates_positive_interval() -> None:
    scheduler = CronScheduler()

    async def noop() -> None:
        return None

    with pytest.raises(ValueError, match="interval_sec must be > 0"):
        scheduler.add_job(name="bad", interval_sec=0, handler=noop)
