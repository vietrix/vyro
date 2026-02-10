from __future__ import annotations

import pytest

from vyro.runtime.security.tenant import TenantIsolationError, TenantIsolationModel


def test_tenant_model_register_and_lookup() -> None:
    model = TenantIsolationModel()
    profile = model.register_tenant(
        "acme",
        scopes={"orders.read", "orders.write"},
        metadata={"tier": "enterprise"},
    )

    assert profile.tenant_id == "acme"
    assert model.get_tenant("acme").metadata["tier"] == "enterprise"


def test_tenant_model_detects_cross_tenant_violation() -> None:
    model = TenantIsolationModel()
    model.register_tenant("acme")
    model.register_tenant("globex")

    with pytest.raises(TenantIsolationError, match="tenant isolation violation"):
        model.ensure_isolated(actor_tenant="acme", resource_tenant="globex")


def test_tenant_model_scope_and_namespace() -> None:
    model = TenantIsolationModel()
    model.register_tenant("acme", scopes={"orders.read"})

    assert model.can_access_scope("acme", "orders.read") is True
    assert model.can_access_scope("acme", "orders.write") is False
    assert model.namespaced_key("acme", "cache:user:1") == "acme:cache:user:1"
