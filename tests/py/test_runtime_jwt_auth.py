from __future__ import annotations

from vyro.runtime.security.jwt_auth import JWTAuthGuard


def test_jwt_auth_guard_issue_and_verify_token() -> None:
    guard = JWTAuthGuard(secret=b"secret-key")
    token = guard.issue("user-1", scopes=["read:users"])
    payload = guard.verify(token)
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert "read:users" in payload["scopes"]


def test_jwt_auth_guard_rejects_expired_token() -> None:
    guard = JWTAuthGuard(secret=b"secret-key")
    token = guard.issue("user-1", ttl_seconds=0)
    assert guard.verify(token) is None


def test_jwt_auth_guard_authorize_checks_required_scopes() -> None:
    guard = JWTAuthGuard(secret=b"secret-key")
    token = guard.issue("user-1", scopes=["read:users", "write:users"])
    assert guard.authorize(token, {"read:users"}) is True
    assert guard.authorize(token, {"admin"}) is False
