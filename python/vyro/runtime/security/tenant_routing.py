from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TenantRouteBinding:
    tenant_id: str
    route_prefix: str


@dataclass(slots=True)
class TenantRoutingConfig:
    prefix_template: str = "/tenants/{tenant_id}"
    aliases: dict[str, str] = field(default_factory=dict)
    enabled: bool = True

    def resolve_tenant_id(self, tenant_id: str) -> str:
        return self.aliases.get(tenant_id, tenant_id)

    def bind(self, tenant_id: str) -> TenantRouteBinding:
        resolved = self.resolve_tenant_id(tenant_id)
        prefix = self.prefix_template.format(tenant_id=resolved).rstrip("/")
        if not prefix.startswith("/"):
            prefix = f"/{prefix}"
        return TenantRouteBinding(tenant_id=resolved, route_prefix=prefix)

    def apply(self, path: str, tenant_id: str | None) -> tuple[str, str | None]:
        if not self.enabled or tenant_id is None:
            return path, None
        binding = self.bind(tenant_id)
        cleaned = path if path.startswith("/") else f"/{path}"
        return f"{binding.route_prefix}{cleaned}", binding.tenant_id
