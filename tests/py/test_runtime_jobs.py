from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.async_ops.jobs import JobRuntime
from vyro.runtime.async_ops.task_trace import current_task_trace


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


def test_job_runtime_injects_trace_context() -> None:
    runtime = JobRuntime()
    seen: list[tuple[dict[str, int], str | None]] = []

    async def handler(payload):  # type: ignore[no-untyped-def]
        ctx = current_task_trace()
        seen.append((payload, ctx.trace_id if ctx is not None else None))

    async def run() -> None:
        runtime.register("trace", handler)
        await runtime.enqueue("trace", {"id": 1})
        await runtime.run_once()

    asyncio.run(run())
    assert seen[0][0] == {"id": 1}
    assert seen[0][1] is not None


def test_job_runtime_uses_provided_trace_id() -> None:
    runtime = JobRuntime()
    seen: list[str | None] = []

    async def handler(payload):  # type: ignore[no-untyped-def]
        del payload
        ctx = current_task_trace()
        seen.append(ctx.trace_id if ctx is not None else None)

    async def run() -> None:
        runtime.register("trace", handler)
        await runtime.enqueue("trace", {"id": 1}, trace_id="trace-abc")
        await runtime.run_once()

    asyncio.run(run())
    assert seen == ["trace-abc"]
