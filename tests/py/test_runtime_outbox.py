from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.data.outbox import InMemoryOutboxStore, OutboxPatternHelper


def test_outbox_stage_and_pending() -> None:
    helper = OutboxPatternHelper()
    helper.stage("user.created", {"id": 1})
    pending = helper.store.pending()
    assert len(pending) == 1
    assert pending[0].topic == "user.created"
    assert pending[0].payload == {"id": 1}


def test_outbox_flush_marks_as_sent() -> None:
    helper = OutboxPatternHelper()
    delivered: list[tuple[str, dict[str, int]]] = []

    async def publisher(topic, payload):  # type: ignore[no-untyped-def]
        delivered.append((topic, payload))

    async def run() -> int:
        helper.stage("order.paid", {"id": 7})
        return await helper.flush(publisher)

    count = asyncio.run(run())
    assert count == 1
    assert delivered == [("order.paid", {"id": 7})]
    assert helper.store.pending() == []


def test_outbox_flush_with_limit() -> None:
    helper = OutboxPatternHelper(store=InMemoryOutboxStore())
    delivered: list[str] = []

    async def publisher(topic, payload):  # type: ignore[no-untyped-def]
        del payload
        delivered.append(topic)

    async def run() -> int:
        helper.stage("a", {"n": 1})
        helper.stage("b", {"n": 2})
        return await helper.flush(publisher, limit=1)

    count = asyncio.run(run())
    assert count == 1
    assert delivered == ["a"]
    assert len(helper.store.pending()) == 1


def test_outbox_store_mark_sent_unknown_message() -> None:
    store = InMemoryOutboxStore()
    with pytest.raises(KeyError, match="unknown outbox message"):
        store.mark_sent(999)
