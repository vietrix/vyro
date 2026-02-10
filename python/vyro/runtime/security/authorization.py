from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AuthorizationCore:
    _role_permissions: dict[str, set[str]] = field(default_factory=dict)
    _abac_rules: dict[str, dict[str, Any]] = field(default_factory=dict)

    def grant(self, role: str, permission: str) -> None:
        self._role_permissions.setdefault(role, set()).add(permission)

    def set_abac_rule(self, permission: str, required_attributes: dict[str, Any]) -> None:
        self._abac_rules[permission] = dict(required_attributes)

    def authorize(
        self,
        *,
        roles: set[str],
        permission: str,
        attributes: dict[str, Any] | None = None,
    ) -> bool:
        allowed_by_role = any(permission in self._role_permissions.get(role, set()) for role in roles)
        if not allowed_by_role:
            return False
        if permission not in self._abac_rules:
            return True
        attrs = attributes or {}
        expected = self._abac_rules[permission]
        return all(attrs.get(key) == value for key, value in expected.items())
