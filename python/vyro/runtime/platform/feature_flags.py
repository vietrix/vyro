from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class FeatureFlagRule:
    enabled: bool = True
    rollout_percent: int = 100
    actors: frozenset[str] = field(default_factory=frozenset)
    tenants: frozenset[str] = field(default_factory=frozenset)


@dataclass(slots=True)
class FeatureFlagEngine:
    _rules: dict[str, FeatureFlagRule] = field(default_factory=dict)

    def set_flag(
        self,
        key: str,
        *,
        enabled: bool = True,
        rollout_percent: int = 100,
        actors: set[str] | None = None,
        tenants: set[str] | None = None,
    ) -> FeatureFlagRule:
        percent = max(0, min(rollout_percent, 100))
        rule = FeatureFlagRule(
            enabled=enabled,
            rollout_percent=percent,
            actors=frozenset(actors or set()),
            tenants=frozenset(tenants or set()),
        )
        self._rules[key] = rule
        return rule

    def get_flag(self, key: str) -> FeatureFlagRule | None:
        return self._rules.get(key)

    def is_enabled(
        self,
        key: str,
        *,
        actor_id: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        rule = self._rules.get(key)
        if rule is None:
            return False
        if not rule.enabled:
            return False

        if rule.tenants and tenant_id not in rule.tenants:
            return False
        if rule.actors and actor_id not in rule.actors:
            return False

        if rule.rollout_percent >= 100:
            return True
        if rule.rollout_percent <= 0:
            return False

        bucket_key = f"{key}:{tenant_id or ''}:{actor_id or ''}"
        bucket = _stable_bucket(bucket_key)
        return bucket < rule.rollout_percent


def _stable_bucket(value: str) -> int:
    digest = sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100
