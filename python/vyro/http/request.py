from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(slots=True)
class RequestView:
    method: str
    path: str
    headers: Mapping[str, str]
    query: Mapping[str, str]
    body: bytes
