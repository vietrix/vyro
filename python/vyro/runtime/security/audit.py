from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class AuditEvent:
    timestamp: datetime
    actor: str
    action: str
    resource: str
    outcome: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SecurityAuditLogger:
    _events: list[AuditEvent] = field(default_factory=list)

    def record(
        self,
        *,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def list_events(
        self,
        *,
        actor: str | None = None,
        action: str | None = None,
    ) -> list[AuditEvent]:
        results = self._events
        if actor is not None:
            results = [item for item in results if item.actor == actor]
        if action is not None:
            results = [item for item in results if item.action == action]
        return list(results)
