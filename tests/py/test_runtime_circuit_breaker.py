from __future__ import annotations

import time

from vyro.runtime.circuit_breaker import OutboundCircuitBreaker


def test_circuit_breaker_opens_after_failure_threshold() -> None:
    breaker = OutboundCircuitBreaker(failure_threshold=2, recovery_timeout_sec=0.2)
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.state == "closed"
    breaker.record_failure()
    assert breaker.state == "open"
    assert breaker.allow_request() is False


def test_circuit_breaker_half_open_and_recovers_on_success() -> None:
    breaker = OutboundCircuitBreaker(
        failure_threshold=1,
        recovery_timeout_sec=0.01,
        half_open_max_calls=1,
    )
    breaker.record_failure()
    assert breaker.state == "open"
    time.sleep(0.02)
    assert breaker.state == "half-open"
    assert breaker.allow_request() is True
    assert breaker.allow_request() is False
    breaker.record_success()
    assert breaker.state == "closed"
