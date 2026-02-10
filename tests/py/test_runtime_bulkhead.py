from __future__ import annotations

import pytest

from vyro.runtime.bulkhead import OutboundBulkhead


def test_bulkhead_isolates_capacity_per_dependency() -> None:
    bulkhead = OutboundBulkhead(default_limit=1)
    assert bulkhead.acquire("payments") is True
    assert bulkhead.acquire("payments") is False
    assert bulkhead.acquire("search") is True
    assert bulkhead.inflight("payments") == 1
    assert bulkhead.inflight("search") == 1


def test_bulkhead_respects_custom_limit_per_dependency() -> None:
    bulkhead = OutboundBulkhead(default_limit=1)
    bulkhead.set_limit("payments", 2)
    assert bulkhead.acquire("payments") is True
    assert bulkhead.acquire("payments") is True
    assert bulkhead.acquire("payments") is False


def test_bulkhead_rejects_invalid_limit() -> None:
    bulkhead = OutboundBulkhead()
    with pytest.raises(ValueError, match="limit must be > 0"):
        bulkhead.set_limit("payments", 0)
