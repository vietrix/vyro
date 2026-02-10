from __future__ import annotations

from vyro.runtime.csrf import CSRFProtector


def test_csrf_protector_issues_and_verifies_token_for_mutating_method() -> None:
    protector = CSRFProtector(secret=b"test-secret")
    token = protector.issue_token("session-1")
    assert protector.verify("session-1", token, method="POST") is True


def test_csrf_protector_rejects_invalid_token() -> None:
    protector = CSRFProtector(secret=b"test-secret")
    assert protector.verify("session-1", "bad.token", method="PUT") is False


def test_csrf_protector_allows_safe_methods_without_token() -> None:
    protector = CSRFProtector(secret=b"test-secret")
    assert protector.verify("session-1", None, method="GET") is True
