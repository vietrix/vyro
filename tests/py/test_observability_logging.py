from __future__ import annotations

import json

from vyro.observability.logging import make_log_record


def test_make_log_record_contains_core_fields() -> None:
    record = make_log_record("info", "boot", service="vyro")
    assert record["level"] == "INFO"
    assert record["message"] == "boot"
    assert record["service"] == "vyro"
    assert "timestamp" in record


def test_log_record_is_json_serializable() -> None:
    record = make_log_record("warn", "retrying", attempts=2)
    encoded = json.dumps(record)
    assert '"level": "WARN"' in encoded
