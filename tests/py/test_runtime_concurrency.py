from __future__ import annotations

from vyro.runtime.concurrency import RouteConcurrencyLimiter


def test_route_concurrency_limiter_default_limit() -> None:
    limiter = RouteConcurrencyLimiter(default_limit=2)
    assert limiter.acquire("/users") is True
    assert limiter.acquire("/users") is True
    assert limiter.acquire("/users") is False
    assert limiter.inflight("/users") == 2
    limiter.release("/users")
    assert limiter.inflight("/users") == 1


def test_route_concurrency_limiter_route_override() -> None:
    limiter = RouteConcurrencyLimiter(default_limit=10)
    limiter.set_limit("/hot", 1)
    assert limiter.acquire("/hot") is True
    assert limiter.acquire("/hot") is False
    limiter.release("/hot")
    assert limiter.acquire("/hot") is True
