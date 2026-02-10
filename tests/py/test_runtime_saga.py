from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.async_ops.saga import SagaOrchestrator, SagaStep, SagaStepFailedError


def test_saga_orchestrator_executes_steps_in_order() -> None:
    orchestrator = SagaOrchestrator()
    calls: list[str] = []

    async def reserve_inventory(payload):  # type: ignore[no-untyped-def]
        calls.append(f"reserve:{payload['order_id']}")

    def charge_payment(payload):  # type: ignore[no-untyped-def]
        calls.append(f"charge:{payload['order_id']}")

    orchestrator.add_step(SagaStep(name="inventory", action=reserve_inventory))
    orchestrator.add_step(SagaStep(name="payment", action=charge_payment))

    result = asyncio.run(orchestrator.run({"order_id": "O-1"}))
    assert result.success is True
    assert result.completed_steps == ("inventory", "payment")
    assert calls == ["reserve:O-1", "charge:O-1"]


def test_saga_orchestrator_compensates_on_failure() -> None:
    orchestrator = SagaOrchestrator()
    calls: list[str] = []

    def reserve(payload):  # type: ignore[no-untyped-def]
        calls.append(f"reserve:{payload['order_id']}")

    async def release(payload):  # type: ignore[no-untyped-def]
        calls.append(f"release:{payload['order_id']}")

    def payment(payload):  # type: ignore[no-untyped-def]
        del payload
        raise RuntimeError("payment gateway timeout")

    orchestrator.add_step(SagaStep(name="inventory", action=reserve, compensate=release))
    orchestrator.add_step(SagaStep(name="payment", action=payment))

    with pytest.raises(SagaStepFailedError, match="payment"):
        asyncio.run(orchestrator.run({"order_id": "O-2"}))

    assert calls == ["reserve:O-2", "release:O-2"]
