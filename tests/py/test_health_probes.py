from __future__ import annotations

from vyro import HealthProbes


def test_health_probes_default_state() -> None:
    probes = HealthProbes()
    assert probes.liveness()["status"] == "ok"
    assert probes.readiness()["status"] == "fail"
    assert probes.startup()["status"] == "fail"


def test_health_probes_state_transitions() -> None:
    probes = HealthProbes()
    probes.mark_started()
    probes.mark_ready()
    assert probes.startup()["status"] == "ok"
    assert probes.readiness()["status"] == "ok"
    probes.mark_not_ready()
    assert probes.readiness()["status"] == "fail"
    probes.mark_unhealthy()
    assert probes.liveness()["status"] == "fail"
    probes.mark_healthy()
    assert probes.liveness()["status"] == "ok"
