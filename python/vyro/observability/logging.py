from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

import typer


def make_log_record(level: str, message: str, **fields: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "message": message,
    }
    for key, value in fields.items():
        if value is not None:
            record[key] = value
    return record


def emit_log(level: str, message: str, *, err: bool = False, **fields: Any) -> None:
    typer.echo(json.dumps(make_log_record(level, message, **fields), ensure_ascii=False), err=err)
