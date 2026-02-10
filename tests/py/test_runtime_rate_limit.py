from __future__ import annotations

import time

from vyro.runtime.rate_limit import TokenBucketRateLimiter


def test_rate_limiter_respects_burst_capacity() -> None:
    limiter = TokenBucketRateLimiter(rate_per_sec=1.0, burst=2)
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is False


def test_rate_limiter_refills_over_time() -> None:
    limiter = TokenBucketRateLimiter(rate_per_sec=20.0, burst=1)
    assert limiter.allow() is True
    assert limiter.allow() is False
    time.sleep(0.06)
    assert limiter.allow() is True
