from __future__ import annotations

import pytest

from vyro.runtime.resilience.retry import RetryPolicy


def test_retry_policy_delay_respects_exponential_backoff_and_cap() -> None:
    policy = RetryPolicy(base_delay_sec=0.1, max_delay_sec=0.25, jitter_ratio=0.0)
    assert policy.next_delay(1) == pytest.approx(0.1)
    assert policy.next_delay(2) == pytest.approx(0.2)
    assert policy.next_delay(3) == pytest.approx(0.25)


def test_retry_policy_adds_jitter_in_expected_range() -> None:
    policy = RetryPolicy(
        base_delay_sec=0.2,
        max_delay_sec=1.0,
        jitter_ratio=0.5,
        _rand=lambda: 1.0,
    )
    assert policy.next_delay(1) == pytest.approx(0.3)


def test_retry_policy_rejects_invalid_attempt_number() -> None:
    policy = RetryPolicy()
    with pytest.raises(ValueError, match="attempt must be >= 1"):
        policy.next_delay(0)
