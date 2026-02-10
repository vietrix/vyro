from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .sse import SSEResponse


@dataclass(slots=True)
class ResponseView:
    status: int = 200
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes | str | dict | list | tuple | SSEResponse | None = b""
