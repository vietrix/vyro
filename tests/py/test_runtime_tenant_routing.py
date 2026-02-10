from __future__ import annotations

from vyro.runtime.tenant_routing import TenantRoutingConfig


def test_tenant_routing_apply_disabled_keeps_path() -> None:
    config = TenantRoutingConfig(enabled=False)
    path, tenant = config.apply("/users", "acme")
    assert path == "/users"
    assert tenant is None


def test_tenant_routing_apply_prefixes_path() -> None:
    config = TenantRoutingConfig(prefix_template="/tenant/{tenant_id}")
    path, tenant = config.apply("/users/:id", "acme")
    assert path == "/tenant/acme/users/:id"
    assert tenant == "acme"


def test_tenant_routing_apply_uses_alias() -> None:
    config = TenantRoutingConfig(aliases={"vtx": "vietrix"})
    path, tenant = config.apply("/health", "vtx")
    assert path == "/tenants/vietrix/health"
    assert tenant == "vietrix"
