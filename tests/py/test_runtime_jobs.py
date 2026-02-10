from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.jobs import JobRuntime


def test_job_runtime_register_enqueue_and_run_once() -> None:
    runtime = JobRuntime()
    seen: list[dict[str, int]] = []

    async def handler(payload):  # type: ignore[no-untyped-def]
        seen.append(payload)

    async def run() -> None:
        runtime.register("send_email", handler)
        await runtime.enqueue("send_email", {"id": 1})
        ran = await runtime.run_once()
        assert ran is True

    asyncio.run(run())
    assert seen == [{"id": 1}]


def test_job_runtime_drain_processes_all_jobs() -> None:
    runtime = JobRuntime()
    counter = {"count": 0}

    async def handler(payload):  # type: ignore[no-untyped-def]
        counter["count"] += payload["n"]

    async def run() -> None:
        runtime.register("sum", handler)
        await runtime.enqueue("sum", {"n": 1})
        await runtime.enqueue("sum", {"n": 2})
        drained = await runtime.drain()
        assert drained == 2

    asyncio.run(run())
    assert counter["count"] == 3


def test_job_runtime_raises_for_unknown_handler() -> None:
    runtime = JobRuntime()

    async def run() -> None:
        await runtime.enqueue("missing", {"x": 1})
        with pytest.raises(KeyError, match="unknown job handler"):
            await runtime.run_once()

    asyncio.run(run())
