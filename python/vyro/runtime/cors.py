from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CORSProfileName = Literal["strict", "standard", "permissive"]


@dataclass(slots=True)
class CORSProfile:
    name: CORSProfileName = "standard"
    allow_origins: tuple[str, ...] = ("*",)
    allow_methods: tuple[str, ...] = ("GET", "POST", "PUT", "DELETE", "OPTIONS")
    allow_headers: tuple[str, ...] = ("content-type", "authorization")
    allow_credentials: bool = False
    max_age: int = 600

    @classmethod
    def preset(cls, name: CORSProfileName) -> CORSProfile:
        if name == "strict":
            return cls(
                name=name,
                allow_origins=(),
                allow_methods=("GET", "POST"),
                allow_headers=("content-type",),
                allow_credentials=False,
                max_age=300,
            )
        if name == "permissive":
            return cls(
                name=name,
                allow_origins=("*",),
                allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
                allow_headers=("*",),
                allow_credentials=False,
                max_age=3600,
            )
        return cls(
            name="standard",
            allow_origins=("*",),
            allow_methods=("GET", "POST", "PUT", "DELETE", "OPTIONS"),
            allow_headers=("content-type", "authorization", "x-request-id"),
            allow_credentials=False,
            max_age=600,
        )

    def apply(
        self,
        *,
        origin: str | None,
        preflight: bool = False,
        request_method: str | None = None,
    ) -> dict[str, str]:
        if not origin:
            return {}
        if not self._origin_allowed(origin):
            return {}

        allow_origin = "*" if "*" in self.allow_origins else origin
        headers = {
            "access-control-allow-origin": allow_origin,
            "vary": "origin",
        }
        if self.allow_credentials:
            headers["access-control-allow-credentials"] = "true"

        if preflight:
            if request_method and request_method.upper() not in self.allow_methods:
                return {}
            headers["access-control-allow-methods"] = ", ".join(self.allow_methods)
            headers["access-control-allow-headers"] = ", ".join(self.allow_headers)
            headers["access-control-max-age"] = str(self.max_age)

        return headers

    def _origin_allowed(self, origin: str) -> bool:
        return "*" in self.allow_origins or origin in self.allow_origins
