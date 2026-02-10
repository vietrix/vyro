from __future__ import annotations

from vyro.runtime.security.api_keys import APIKeyManager


def test_api_key_manager_issue_and_verify() -> None:
    manager = APIKeyManager()
    plaintext, record = manager.issue(metadata={"owner": "svc-a"})
    assert plaintext.startswith("vyro_")
    assert manager.verify(record.key_id, plaintext) is True
    assert manager.verify(record.key_id, "wrong") is False


def test_api_key_manager_rotate_updates_hash_and_triggers_hook() -> None:
    manager = APIKeyManager()
    _, record = manager.issue()
    rotated: list[str] = []
    manager.set_hooks(on_rotate=lambda r: rotated.append(r.key_id))
    old_hash = record.key_hash
    new_plain, updated = manager.rotate(record.key_id)
    assert updated.key_hash != old_hash
    assert manager.verify(record.key_id, new_plain) is True
    assert rotated == [record.key_id]


def test_api_key_manager_revoke_disables_key_and_triggers_hook() -> None:
    manager = APIKeyManager()
    plaintext, record = manager.issue()
    revoked: list[str] = []
    manager.set_hooks(on_revoke=lambda r: revoked.append(r.key_id))
    manager.revoke(record.key_id)
    assert manager.verify(record.key_id, plaintext) is False
    assert revoked == [record.key_id]
