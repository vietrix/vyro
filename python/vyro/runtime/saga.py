from __future__ import annotations

from dataclasses import dataclass, field
from inspect import isawaitable
from typing import Any, Awaitable, Callable


SagaAction = Callable[[dict[str, Any]], Awaitable[None] | None]


class SagaError(RuntimeError):
    pass


class SagaStepFailedError(SagaError):
    def __init__(self, step: str, cause: Exception) -> None:
        super().__init__(f"saga step failed: {step} ({cause})")
        self.step = step
        self.cause = cause


@dataclass(frozen=True, slots=True)
class SagaStep:
    name: str
    action: SagaAction
    compensate: SagaAction | None = None


@dataclass(frozen=True, slots=True)
class SagaResult:
    success: bool
    completed_steps: tuple[str, ...]
    compensated_steps: tuple[str, ...]


@dataclass(slots=True)
class SagaOrchestrator:
    _steps: list[SagaStep] = field(default_factory=list)

    def add_step(self, step: SagaStep) -> None:
        self._steps.append(step)

    async def run(self, payload: dict[str, Any]) -> SagaResult:
        completed: list[SagaStep] = []
        compensated: list[str] = []
        state = dict(payload)

        for step in self._steps:
            try:
                result = step.action(state)
                if isawaitable(result):
                    await result
                completed.append(step)
            except Exception as exc:  # noqa: BLE001
                for done in reversed(completed):
                    if done.compensate is None:
                        continue
                    compensate_result = done.compensate(state)
                    if isawaitable(compensate_result):
                        await compensate_result
                    compensated.append(done.name)
                raise SagaStepFailedError(step=step.name, cause=exc) from exc

        return SagaResult(
            success=True,
            completed_steps=tuple(step.name for step in completed),
            compensated_steps=tuple(compensated),
        )
