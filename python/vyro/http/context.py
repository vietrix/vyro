from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4


CORRELATION_ID_HEADER = "x-correlation-id"
TRACEPARENT_HEADER = "traceparent"


@dataclass(slots=True)
class Context:
    headers: Mapping[str, str]
    query: Mapping[str, str]
    path_params: Mapping[str, str]
    _body: bytes
    _extensions: dict[str, Any]

    @classmethod
    def from_native(cls, payload: dict[str, Any]) -> "Context":
        headers = {k.lower(): v for k, v in dict(payload.get("headers", {})).items()}
        headers.setdefault(CORRELATION_ID_HEADER, uuid4().hex)
        headers.setdefault(
            TRACEPARENT_HEADER,
            _build_traceparent(headers[CORRELATION_ID_HEADER]),
        )
        return cls(
            headers=MappingProxyType(headers),
            query=MappingProxyType(dict(payload.get("query", {}))),
            path_params=MappingProxyType(dict(payload.get("path_params", {}))),
            _body=payload.get("body", b""),
            _extensions={},
        )

    def body_bytes(self) -> bytes:
        return self._body

    def json(self) -> Any:
        if not self._body:
            return None
        return json.loads(self._body.decode("utf-8"))

    def set_extension(self, key: str, value: Any) -> None:
        self._extensions[key] = value

    def get_extension(self, key: str, default: Any = None) -> Any:
        return self._extensions.get(key, default)

    @property
    def extensions(self) -> Mapping[str, Any]:
        return MappingProxyType(self._extensions)

    @property
    def correlation_id(self) -> str:
        return str(self.headers[CORRELATION_ID_HEADER])

    @property
    def traceparent(self) -> str:
        return str(self.headers[TRACEPARENT_HEADER])


def _build_traceparent(seed: str) -> str:
    trace_id = (seed.replace("-", "") + uuid4().hex)[:32]
    span_id = uuid4().hex[:16]
    return f"00-{trace_id}-{span_id}-01"
