from __future__ import annotations

from vyro.runtime.resilience.backpressure import BackpressureController


def test_backpressure_acquire_release_flow() -> None:
    controller = BackpressureController(max_inflight=2)
    assert controller.acquire() is True
    assert controller.acquire() is True
    assert controller.acquire() is False
    assert controller.inflight == 2
    controller.release()
    assert controller.inflight == 1
    assert controller.acquire() is True


def test_backpressure_reject_when_limit_reached() -> None:
    controller = BackpressureController(max_inflight=1)
    assert controller.should_reject() is False
    assert controller.acquire() is True
    assert controller.should_reject() is True
