from __future__ import annotations

from vyro.runtime.discovery import (
    EnvDiscoveryAdapter,
    ServiceDiscoveryRegistry,
    ServiceEndpoint,
    StaticDiscoveryAdapter,
)


def test_static_discovery_adapter_resolve() -> None:
    adapter = StaticDiscoveryAdapter()
    adapter.register("users", ServiceEndpoint(service="users", host="127.0.0.1", port=9001))
    items = adapter.resolve("users")
    assert len(items) == 1
    assert items[0].url == "http://127.0.0.1:9001"


def test_env_discovery_adapter_resolve(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    adapter = EnvDiscoveryAdapter(prefix="TEST_DISCOVERY_")
    monkeypatch.setenv("TEST_DISCOVERY_ORDERS", "10.0.0.1:8080,10.0.0.2:8081")
    items = adapter.resolve("orders")
    assert [item.url for item in items] == ["http://10.0.0.1:8080", "http://10.0.0.2:8081"]


def test_service_discovery_registry_aggregates_adapters(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    static_adapter = StaticDiscoveryAdapter()
    static_adapter.register("billing", ServiceEndpoint(service="billing", host="127.0.0.1", port=7000))

    env_adapter = EnvDiscoveryAdapter(prefix="TEST_DISCOVERY_")
    monkeypatch.setenv("TEST_DISCOVERY_BILLING", "10.1.0.1:7100")

    registry = ServiceDiscoveryRegistry()
    registry.register_adapter(static_adapter)
    registry.register_adapter(env_adapter)

    items = registry.resolve("billing")
    assert len(items) == 2
