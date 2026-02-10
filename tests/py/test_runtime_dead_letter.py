from __future__ import annotations

import asyncio

from vyro.runtime.dead_letter import DeadLetterQueue, JobRetryExecutor
from vyro.runtime.task_trace import current_task_trace


def test_job_retry_executor_retries_then_succeeds() -> None:
    executor = JobRetryExecutor(max_retries=3)
    calls = {"n": 0}

    async def flaky(payload):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("temporary")

    ok = asyncio.run(executor.run("job", {"x": 1}, flaky))
    assert ok is True
    assert calls["n"] == 3
    assert executor.dead_letter_queue.items() == []


def test_job_retry_executor_moves_to_dead_letter_after_exhaustion() -> None:
    queue = DeadLetterQueue()
    executor = JobRetryExecutor(max_retries=1, dead_letter_queue=queue)

    async def always_fail(payload):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    ok = asyncio.run(executor.run("send_email", {"id": 1}, always_fail))
    assert ok is False
    items = queue.items()
    assert len(items) == 1
    assert items[0].job_name == "send_email"
    assert items[0].attempts == 2
    assert items[0].trace_id


def test_job_retry_executor_preserves_given_trace_id() -> None:
    queue = DeadLetterQueue()
    executor = JobRetryExecutor(max_retries=0, dead_letter_queue=queue)

    async def always_fail(payload):  # type: ignore[no-untyped-def]
        del payload
        raise ValueError("boom")

    ok = asyncio.run(executor.run("sync", {"id": 9}, always_fail, trace_id="trace-fixed"))
    assert ok is False
    item = queue.items()[0]
    assert item.trace_id == "trace-fixed"


def test_job_retry_executor_sets_trace_scope_for_handler() -> None:
    executor = JobRetryExecutor(max_retries=0)
    seen: list[str | None] = []

    async def always_fail(payload):  # type: ignore[no-untyped-def]
        del payload
        ctx = current_task_trace()
        seen.append(ctx.trace_id if ctx is not None else None)
        raise ValueError("boom")

    asyncio.run(executor.run("sync", {"id": 9}, always_fail, trace_id="trace-scope"))
    assert seen == ["trace-scope"]
