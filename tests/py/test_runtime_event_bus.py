from __future__ import annotations

import asyncio

from vyro.runtime.async_ops.event_bus import InternalEventBus


def test_event_bus_publish_to_sync_subscriber() -> None:
    bus = InternalEventBus()
    seen: list[tuple[str, int, str | None]] = []

    def on_user_created(event):  # type: ignore[no-untyped-def]
        seen.append((event.name, event.payload["id"], event.trace_id))

    bus.subscribe("user.created", on_user_created)
    delivered = asyncio.run(bus.publish("user.created", {"id": 7}, trace_id="trace-1"))

    assert delivered == 1
    assert seen == [("user.created", 7, "trace-1")]


def test_event_bus_publish_to_async_subscriber() -> None:
    bus = InternalEventBus()
    seen: list[str] = []

    async def on_order_paid(event):  # type: ignore[no-untyped-def]
        seen.append(event.payload["order_id"])

    bus.subscribe("order.paid", on_order_paid)
    delivered = asyncio.run(bus.publish("order.paid", {"order_id": "A-1"}))

    assert delivered == 1
    assert seen == ["A-1"]


def test_event_bus_returns_zero_when_no_subscribers() -> None:
    bus = InternalEventBus()
    delivered = asyncio.run(bus.publish("missing", {"ok": True}))
    assert delivered == 0
