from __future__ import annotations

import json
import os

from vyro.observability.logging import SamplingPolicy, make_log_record, should_emit


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


def test_sampling_policy_is_deterministic_for_key() -> None:
    policy = SamplingPolicy(info_rate=0.5, warn_rate=1.0, error_rate=1.0)
    a = should_emit("info", "same-key", policy)
    b = should_emit("info", "same-key", policy)
    assert a is b


def test_sampling_respects_zero_and_one_rates() -> None:
    drop_all = SamplingPolicy(info_rate=0.0, warn_rate=0.0, error_rate=0.0)
    keep_all = SamplingPolicy(info_rate=1.0, warn_rate=1.0, error_rate=1.0)
    assert should_emit("info", "k1", drop_all) is False
    assert should_emit("warn", "k2", drop_all) is False
    assert should_emit("error", "k3", drop_all) is False
    assert should_emit("info", "k4", keep_all) is True


def test_log_record_redacts_sensitive_fields() -> None:
    record = make_log_record("info", "auth", password="secret", token="abc", safe="ok")
    assert record["password"] == "***REDACTED***"
    assert record["token"] == "***REDACTED***"
    assert record["safe"] == "ok"


def test_log_record_redacts_configured_keys() -> None:
    old = os.environ.get("VYRO_LOG_REDACT_KEYS")
    os.environ["VYRO_LOG_REDACT_KEYS"] = "session_id, private_note"
    try:
        record = make_log_record("info", "evt", session_id="s1", private_note="x", other="ok")
    finally:
        if old is None:
            os.environ.pop("VYRO_LOG_REDACT_KEYS", None)
        else:
            os.environ["VYRO_LOG_REDACT_KEYS"] = old
    assert record["session_id"] == "***REDACTED***"
    assert record["private_note"] == "***REDACTED***"
    assert record["other"] == "ok"
