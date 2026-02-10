from __future__ import annotations

import pytest

from vyro.runtime.timeout_budget import TimeoutBudget


def test_timeout_budget_tracks_remaining_time() -> None:
    now = [100.0]
    budget = TimeoutBudget(timeout_sec=10.0, _clock=lambda: now[0])
    assert budget.remaining_sec == pytest.approx(10.0)
    now[0] = 104.5
    assert budget.remaining_sec == pytest.approx(5.5)
    assert budget.is_expired() is False
    now[0] = 111.0
    assert budget.is_expired() is True


def test_timeout_budget_child_is_clamped_to_parent_remaining() -> None:
    now = [50.0]
    budget = TimeoutBudget(timeout_sec=5.0, _clock=lambda: now[0])
    now[0] = 52.0
    child = budget.child(timeout_sec=10.0)
    assert child.timeout_sec == pytest.approx(3.0)


def test_timeout_budget_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError, match="timeout_sec must be > 0"):
        TimeoutBudget(timeout_sec=0)
