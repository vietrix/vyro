from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any

import typer


DEFAULT_REDACT_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "api_key",
}


@dataclass(slots=True, frozen=True)
class SamplingPolicy:
    info_rate: float = 1.0
    warn_rate: float = 1.0
    error_rate: float = 1.0

    def rate_for(self, level: str) -> float:
        normalized = level.upper()
        if normalized == "INFO":
            return self.info_rate
        if normalized == "WARN":
            return self.warn_rate
        if normalized == "ERROR":
            return self.error_rate
        return 1.0


def make_log_record(level: str, message: str, **fields: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "message": message,
    }
    for key, value in fields.items():
        if value is not None:
            record[key] = _sanitize_field(key, value)
    return record


def should_emit(level: str, sample_key: str, policy: SamplingPolicy) -> bool:
    rate = policy.rate_for(level)
    if rate <= 0:
        return False
    if rate >= 1:
        return True
    digest = hashlib.sha1(sample_key.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=False) / float(2**64 - 1)
    return value < rate


def emit_log(
    level: str,
    message: str,
    *,
    err: bool = False,
    sampling_policy: SamplingPolicy | None = None,
    sample_key: str | None = None,
    **fields: Any,
) -> None:
    policy = sampling_policy or SamplingPolicy()
    key = sample_key or message
    if not should_emit(level, key, policy):
        return
    typer.echo(json.dumps(make_log_record(level, message, **fields), ensure_ascii=False), err=err)


def _sanitize_field(key: str, value: Any) -> Any:
    redacted_keys = set(DEFAULT_REDACT_KEYS)
    extra = os.getenv("VYRO_LOG_REDACT_KEYS", "")
    for raw in extra.split(","):
        cleaned = raw.strip().lower()
        if cleaned:
            redacted_keys.add(cleaned)
    if key.lower() in redacted_keys:
        return "***REDACTED***"
    if isinstance(value, dict):
        return {k: _sanitize_field(str(k), v) for k, v in value.items()}
    return value
