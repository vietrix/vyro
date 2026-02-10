from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(slots=True)
class Context:
    headers: Mapping[str, str]
    query: Mapping[str, str]
    path_params: Mapping[str, str]
    _body: bytes
    _extensions: dict[str, Any]

    @classmethod
    def from_native(cls, payload: dict[str, Any]) -> "Context":
        return cls(
            headers=MappingProxyType(dict(payload.get("headers", {}))),
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
