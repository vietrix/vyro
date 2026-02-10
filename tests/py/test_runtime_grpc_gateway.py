from __future__ import annotations

import pytest

from vyro.runtime.edge.grpc_gateway import GrpcGateway, GrpcRoute


def test_grpc_gateway_register_and_resolve_route() -> None:
    gateway = GrpcGateway()
    route = GrpcRoute(
        http_method="POST",
        http_path="/v1/users",
        grpc_service="users.v1.UsersService",
        grpc_method="CreateUser",
    )
    gateway.register(route)
    assert gateway.resolve("POST", "/v1/users") == route


def test_grpc_gateway_transcodes_http_to_grpc_call_descriptor() -> None:
    gateway = GrpcGateway()
    gateway.register(
        GrpcRoute(
            http_method="GET",
            http_path="/v1/users/{id}",
            grpc_service="users.v1.UsersService",
            grpc_method="GetUser",
        )
    )
    service, method, payload = gateway.transcode_request("GET", "/v1/users/{id}", {"id": "42"})
    assert service == "users.v1.UsersService"
    assert method == "GetUser"
    assert payload == {"id": "42"}


def test_grpc_gateway_raises_for_unmapped_route() -> None:
    gateway = GrpcGateway()
    with pytest.raises(KeyError, match="no gRPC route mapped"):
        gateway.transcode_request("POST", "/v1/unknown", {})
