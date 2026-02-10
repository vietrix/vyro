from __future__ import annotations

import time

import pytest

from vyro.runtime.resilience.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter


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


def test_multi_key_rate_limiter_tracks_each_key_tuple_independently() -> None:
    limiter = MultiKeyRateLimiter(rate_per_sec=1.0, burst=1)
    assert limiter.allow("ip:127.0.0.1", "user:42") is True
    assert limiter.allow("ip:127.0.0.1", "user:42") is False
    assert limiter.allow("ip:127.0.0.1", "user:99") is True


def test_multi_key_rate_limiter_requires_at_least_one_key() -> None:
    limiter = MultiKeyRateLimiter(rate_per_sec=1.0, burst=1)
    with pytest.raises(ValueError, match="at least one key is required"):
        limiter.allow()
