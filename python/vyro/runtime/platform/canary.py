from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class CanaryRule:
    route_key: str
    canary_percent: int
    sticky_by: str = "actor"
    canary_actors: frozenset[str] = field(default_factory=frozenset)


@dataclass(slots=True)
class CanaryRoutingControls:
    _rules: dict[str, CanaryRule] = field(default_factory=dict)

    def set_rule(
        self,
        route_key: str,
        *,
        canary_percent: int,
        sticky_by: str = "actor",
        canary_actors: set[str] | None = None,
    ) -> CanaryRule:
        percent = max(0, min(100, canary_percent))
        rule = CanaryRule(
            route_key=route_key,
            canary_percent=percent,
            sticky_by=sticky_by,
            canary_actors=frozenset(canary_actors or set()),
        )
        self._rules[route_key] = rule
        return rule

    def get_rule(self, route_key: str) -> CanaryRule | None:
        return self._rules.get(route_key)

    def select_variant(
        self,
        route_key: str,
        *,
        actor_id: str | None = None,
        tenant_id: str | None = None,
        request_id: str | None = None,
    ) -> str:
        rule = self._rules.get(route_key)
        if rule is None:
            return "primary"
        if actor_id is not None and actor_id in rule.canary_actors:
            return "canary"
        if rule.canary_percent <= 0:
            return "primary"
        if rule.canary_percent >= 100:
            return "canary"

        subject = _resolve_subject(rule.sticky_by, actor_id=actor_id, tenant_id=tenant_id, request_id=request_id)
        bucket = _stable_bucket(f"{route_key}:{subject}")
        if bucket < rule.canary_percent:
            return "canary"
        return "primary"


def _resolve_subject(
    sticky_by: str,
    *,
    actor_id: str | None,
    tenant_id: str | None,
    request_id: str | None,
) -> str:
    if sticky_by == "tenant":
        return tenant_id or ""
    if sticky_by == "request":
        return request_id or ""
    return actor_id or ""


def _stable_bucket(value: str) -> int:
    digest = sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100
