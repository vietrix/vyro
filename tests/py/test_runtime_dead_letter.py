from __future__ import annotations

import asyncio

from vyro.runtime.dead_letter import DeadLetterQueue, JobRetryExecutor


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
