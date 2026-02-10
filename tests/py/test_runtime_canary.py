from __future__ import annotations

from vyro.runtime.canary import CanaryRoutingControls


def test_canary_defaults_to_primary_without_rule() -> None:
    controls = CanaryRoutingControls()
    assert controls.select_variant("GET:/users/:id", actor_id="u1") == "primary"


def test_canary_supports_actor_override() -> None:
    controls = CanaryRoutingControls()
    controls.set_rule("GET:/users/:id", canary_percent=0, canary_actors={"u-canary"})
    assert controls.select_variant("GET:/users/:id", actor_id="u-canary") == "canary"
    assert controls.select_variant("GET:/users/:id", actor_id="u-normal") == "primary"


def test_canary_hundred_percent_routes_all_to_canary() -> None:
    controls = CanaryRoutingControls()
    controls.set_rule("GET:/health", canary_percent=100)
    assert controls.select_variant("GET:/health", actor_id="a1") == "canary"


def test_canary_percent_is_stable_for_same_subject() -> None:
    controls = CanaryRoutingControls()
    controls.set_rule("GET:/checkout", canary_percent=25, sticky_by="tenant")

    first = controls.select_variant("GET:/checkout", tenant_id="acme")
    second = controls.select_variant("GET:/checkout", tenant_id="acme")
    assert first == second
