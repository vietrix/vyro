from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(slots=True)
class Context:
    headers: Mapping[str, str]
    query: Mapping[str, str]
    path_params: Mapping[str, str]
    _body: bytes

    @classmethod
    def from_native(cls, payload: dict[str, Any]) -> "Context":
        return cls(
            headers=dict(payload.get("headers", {})),
            query=dict(payload.get("query", {})),
            path_params=dict(payload.get("path_params", {})),
            _body=payload.get("body", b""),
        )

    def body_bytes(self) -> bytes:
        return self._body

    def json(self) -> Any:
        if not self._body:
            return None
        return json.loads(self._body.decode("utf-8"))
