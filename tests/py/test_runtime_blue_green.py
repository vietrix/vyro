from __future__ import annotations

from vyro.runtime.platform.blue_green import BlueGreenRolloutHelper


def test_blue_green_defaults_to_blue() -> None:
    helper = BlueGreenRolloutHelper()
    assert helper.state.active_color == "blue"
    assert helper.select_color("u1") == "blue"


def test_blue_green_promote_to_green() -> None:
    helper = BlueGreenRolloutHelper()
    helper.promote("green")
    assert helper.state.active_color == "green"
    assert helper.state.traffic_to_green_percent == 100
    assert helper.select_color("u1") == "green"


def test_blue_green_supports_actor_pinning() -> None:
    helper = BlueGreenRolloutHelper()
    helper.set_traffic_to_green(0)
    helper.pin_actor("canary-user", "green")
    assert helper.select_color("canary-user") == "green"
    assert helper.select_color("normal-user") == "blue"
    helper.unpin_actor("canary-user")
    assert helper.select_color("canary-user") == "blue"


def test_blue_green_percent_selection_is_stable() -> None:
    helper = BlueGreenRolloutHelper()
    helper.set_traffic_to_green(35)
    first = helper.select_color("sticky-user")
    second = helper.select_color("sticky-user")
    assert first == second
