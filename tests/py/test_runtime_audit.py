from __future__ import annotations

from vyro.runtime.security.audit import SecurityAuditLogger


def test_security_audit_logger_records_event() -> None:
    logger = SecurityAuditLogger()
    event = logger.record(
        actor="user:1",
        action="auth.login",
        resource="session",
        outcome="success",
        metadata={"ip": "127.0.0.1"},
    )
    assert event.actor == "user:1"
    assert event.metadata["ip"] == "127.0.0.1"
    assert len(logger.list_events()) == 1


def test_security_audit_logger_filters_by_actor_and_action() -> None:
    logger = SecurityAuditLogger()
    logger.record(actor="user:1", action="auth.login", resource="session", outcome="success")
    logger.record(actor="user:2", action="auth.login", resource="session", outcome="success")
    logger.record(actor="user:1", action="auth.logout", resource="session", outcome="success")
    assert len(logger.list_events(actor="user:1")) == 2
    assert len(logger.list_events(action="auth.login")) == 2
    assert len(logger.list_events(actor="user:1", action="auth.login")) == 1
