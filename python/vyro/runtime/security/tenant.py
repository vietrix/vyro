from __future__ import annotations

from dataclasses import dataclass, field


class TenantIsolationError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class TenantProfile:
    tenant_id: str
    scopes: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class TenantIsolationModel:
    _tenants: dict[str, TenantProfile] = field(default_factory=dict)

    def register_tenant(
        self,
        tenant_id: str,
        *,
        scopes: set[str] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> TenantProfile:
        profile = TenantProfile(
            tenant_id=tenant_id,
            scopes=frozenset(scopes or set()),
            metadata=dict(metadata or {}),
        )
        self._tenants[tenant_id] = profile
        return profile

    def get_tenant(self, tenant_id: str) -> TenantProfile:
        profile = self._tenants.get(tenant_id)
        if profile is None:
            raise KeyError(f"unknown tenant: {tenant_id}")
        return profile

    def ensure_isolated(self, *, actor_tenant: str, resource_tenant: str) -> None:
        if actor_tenant != resource_tenant:
            raise TenantIsolationError(
                f"tenant isolation violation: actor={actor_tenant} resource={resource_tenant}"
            )

    def can_access_scope(self, tenant_id: str, scope: str) -> bool:
        profile = self.get_tenant(tenant_id)
        return scope in profile.scopes

    def namespaced_key(self, tenant_id: str, key: str) -> str:
        self.get_tenant(tenant_id)
        return f"{tenant_id}:{key}"
