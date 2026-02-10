from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GrpcRoute:
    http_method: str
    http_path: str
    grpc_service: str
    grpc_method: str
    timeout_sec: float = 5.0


@dataclass(slots=True)
class GrpcGateway:
    _routes: dict[tuple[str, str], GrpcRoute] = field(default_factory=dict)

    def register(self, route: GrpcRoute) -> None:
        key = (route.http_method.upper(), route.http_path)
        self._routes[key] = route

    def resolve(self, http_method: str, http_path: str) -> GrpcRoute | None:
        return self._routes.get((http_method.upper(), http_path))

    def transcode_request(
        self,
        http_method: str,
        http_path: str,
        payload: dict[str, Any] | None = None,
    ) -> tuple[str, str, dict[str, Any]]:
        route = self.resolve(http_method, http_path)
        if route is None:
            raise KeyError(f"no gRPC route mapped for {http_method} {http_path}")
        return route.grpc_service, route.grpc_method, payload or {}
