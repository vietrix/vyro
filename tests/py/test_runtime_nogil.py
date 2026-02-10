from __future__ import annotations

from vyro.runtime.platform.nogil import NoGILWorkerTuner


def test_nogil_tuner_balanced_profile() -> None:
    tuner = NoGILWorkerTuner()
    profile = tuner.recommend(cpu_count=8, workload="balanced")
    assert profile.mode == "balanced"
    assert profile.workers == 8
    assert profile.tokio_worker_threads == 8
    assert profile.python_threads == 8


def test_nogil_tuner_cpu_profile() -> None:
    tuner = NoGILWorkerTuner()
    profile = tuner.recommend(cpu_count=8, workload="cpu")
    assert profile.workers == 8
    assert profile.python_threads == 4


def test_nogil_tuner_io_profile() -> None:
    tuner = NoGILWorkerTuner()
    profile = tuner.recommend(cpu_count=4, workload="io")
    assert profile.workers == 8
    assert profile.tokio_worker_threads == 8
