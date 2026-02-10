from __future__ import annotations

from vyro.runtime.platform.feature_flags import FeatureFlagEngine


def test_flag_defaults_to_disabled_when_missing() -> None:
    engine = FeatureFlagEngine()
    assert engine.is_enabled("beta.endpoint") is False


def test_flag_can_be_enabled_globally() -> None:
    engine = FeatureFlagEngine()
    engine.set_flag("beta.endpoint", enabled=True)
    assert engine.is_enabled("beta.endpoint") is True


def test_flag_can_be_limited_by_tenant_and_actor() -> None:
    engine = FeatureFlagEngine()
    engine.set_flag(
        "billing.v2",
        enabled=True,
        tenants={"acme"},
        actors={"user-1"},
    )
    assert engine.is_enabled("billing.v2", tenant_id="acme", actor_id="user-1") is True
    assert engine.is_enabled("billing.v2", tenant_id="acme", actor_id="user-2") is False
    assert engine.is_enabled("billing.v2", tenant_id="globex", actor_id="user-1") is False


def test_flag_rollout_is_deterministic_for_same_subject() -> None:
    engine = FeatureFlagEngine()
    engine.set_flag("search.v3", enabled=True, rollout_percent=15)

    first = engine.is_enabled("search.v3", tenant_id="acme", actor_id="user-9")
    second = engine.is_enabled("search.v3", tenant_id="acme", actor_id="user-9")
    assert first == second


def test_flag_rollout_zero_and_hundred_bounds() -> None:
    engine = FeatureFlagEngine()
    engine.set_flag("x.zero", enabled=True, rollout_percent=0)
    engine.set_flag("x.full", enabled=True, rollout_percent=100)
    assert engine.is_enabled("x.zero", actor_id="u1") is False
    assert engine.is_enabled("x.full", actor_id="u1") is True
