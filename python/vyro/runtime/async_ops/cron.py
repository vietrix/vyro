from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import monotonic
from typing import Awaitable, Callable


CronHandler = Callable[[], Awaitable[None]]


@dataclass(slots=True)
class CronJob:
    name: str
    interval_sec: float
    handler: CronHandler
    next_run_at: float = field(default_factory=monotonic)


@dataclass(slots=True)
class CronScheduler:
    _jobs: list[CronJob] = field(default_factory=list)

    def add_job(self, *, name: str, interval_sec: float, handler: CronHandler) -> CronJob:
        if interval_sec <= 0:
            raise ValueError("interval_sec must be > 0")
        job = CronJob(name=name, interval_sec=interval_sec, handler=handler, next_run_at=monotonic())
        self._jobs.append(job)
        return job

    async def run_pending(self) -> int:
        now = monotonic()
        ran = 0
        for job in self._jobs:
            if now < job.next_run_at:
                continue
            await job.handler()
            job.next_run_at = monotonic() + job.interval_sec
            ran += 1
        return ran

    async def run_once(self, *, idle_sleep_sec: float = 0.01) -> int:
        ran = await self.run_pending()
        if ran == 0:
            await asyncio.sleep(idle_sleep_sec)
        return ran
