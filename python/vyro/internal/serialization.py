from __future__ import annotations

import json
from typing import Any


def to_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")
