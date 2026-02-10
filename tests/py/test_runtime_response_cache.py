from __future__ import annotations

import time

from vyro.runtime.response_cache import ResponseCachePolicy, ResponseCacheService


def test_response_cache_policy_uses_route_specific_ttl() -> None:
    policy = ResponseCachePolicy(default_ttl_sec=10.0)
    policy.set_ttl(method="GET", route="/users", ttl_sec=1.0)
    assert policy.ttl_for(method="GET", route="/users") == 1.0
    assert policy.ttl_for(method="GET", route="/health") == 10.0


def test_response_cache_service_set_and_get() -> None:
    service = ResponseCacheService()
    service.policy.default_ttl_sec = 10.0
    service.set(method="GET", path="/users", response={"ok": True})
    assert service.get(method="GET", path="/users") == {"ok": True}


def test_response_cache_service_respects_ttl_expiry() -> None:
    service = ResponseCacheService()
    service.policy.set_ttl(method="GET", route="/temp", ttl_sec=0.01)
    service.set(method="GET", path="/temp", response={"ok": True})
    time.sleep(0.02)
    assert service.get(method="GET", path="/temp") is None
