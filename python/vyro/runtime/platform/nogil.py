from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NoGILTuningProfile:
    mode: str
    cpu_count: int
    workers: int
    tokio_worker_threads: int
    python_threads: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "mode": self.mode,
            "cpu_count": self.cpu_count,
            "workers": self.workers,
            "tokio_worker_threads": self.tokio_worker_threads,
            "python_threads": self.python_threads,
        }


@dataclass(slots=True)
class NoGILWorkerTuner:
    def recommend(self, *, cpu_count: int, workload: str = "balanced") -> NoGILTuningProfile:
        cpu = max(1, int(cpu_count))
        mode = workload.strip().lower()

        if mode == "io":
            workers = max(2, cpu * 2)
            tokio_threads = max(2, cpu * 2)
            python_threads = max(2, cpu)
        elif mode == "cpu":
            workers = max(1, cpu)
            tokio_threads = max(1, cpu)
            python_threads = max(1, cpu // 2)
        else:
            mode = "balanced"
            workers = max(1, cpu)
            tokio_threads = max(2, cpu)
            python_threads = max(1, cpu)

        return NoGILTuningProfile(
            mode=mode,
            cpu_count=cpu,
            workers=workers,
            tokio_worker_threads=tokio_threads,
            python_threads=python_threads,
        )
