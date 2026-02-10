from __future__ import annotations

from datetime import datetime, timedelta, timezone

from vyro.runtime.shutdown import GracefulShutdownPolicy


def test_shutdown_policy_deadline_from_start() -> None:
    policy = GracefulShutdownPolicy(timeout_seconds=10)
    start = datetime(2026, 2, 10, 0, 0, tzinfo=timezone.utc)
    assert policy.deadline(start) == start + timedelta(seconds=10)


def test_shutdown_policy_timeout_detection() -> None:
    policy = GracefulShutdownPolicy(timeout_seconds=5)
    start = datetime(2026, 2, 10, 0, 0, tzinfo=timezone.utc)
    assert policy.has_timed_out(start, start + timedelta(seconds=6)) is True
    assert policy.has_timed_out(start, start + timedelta(seconds=4)) is False
