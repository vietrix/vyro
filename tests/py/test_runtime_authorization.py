from __future__ import annotations

from vyro.runtime.security.authorization import AuthorizationCore


def test_authorization_core_grants_rbac_permissions() -> None:
    authz = AuthorizationCore()
    authz.grant("admin", "users:read")
    assert authz.authorize(roles={"admin"}, permission="users:read") is True
    assert authz.authorize(roles={"viewer"}, permission="users:read") is False


def test_authorization_core_enforces_abac_rule_when_defined() -> None:
    authz = AuthorizationCore()
    authz.grant("editor", "users:update")
    authz.set_abac_rule("users:update", {"tenant_id": "t1"})
    assert authz.authorize(
        roles={"editor"},
        permission="users:update",
        attributes={"tenant_id": "t1"},
    ) is True
    assert authz.authorize(
        roles={"editor"},
        permission="users:update",
        attributes={"tenant_id": "t2"},
    ) is False
