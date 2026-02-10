from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


@dataclass(slots=True)
class APIKeyRecord:
    key_id: str
    key_hash: str
    created_at: datetime
    revoked: bool = False
    metadata: dict[str, str] = field(default_factory=dict)


RotationHook = Callable[[APIKeyRecord], None]


@dataclass(slots=True)
class APIKeyManager:
    _keys: dict[str, APIKeyRecord] = field(default_factory=dict)
    _on_rotate: RotationHook | None = None
    _on_revoke: RotationHook | None = None

    def set_hooks(
        self,
        *,
        on_rotate: RotationHook | None = None,
        on_revoke: RotationHook | None = None,
    ) -> None:
        self._on_rotate = on_rotate
        self._on_revoke = on_revoke

    def issue(self, *, metadata: dict[str, str] | None = None) -> tuple[str, APIKeyRecord]:
        key_id = secrets.token_hex(8)
        plaintext = f"vyro_{secrets.token_urlsafe(24)}"
        record = APIKeyRecord(
            key_id=key_id,
            key_hash=self._hash(plaintext),
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._keys[key_id] = record
        return plaintext, record

    def rotate(self, key_id: str) -> tuple[str, APIKeyRecord]:
        existing = self._keys.get(key_id)
        if existing is None:
            raise KeyError(f"unknown api key id: {key_id}")
        plaintext = f"vyro_{secrets.token_urlsafe(24)}"
        existing.key_hash = self._hash(plaintext)
        existing.revoked = False
        if self._on_rotate is not None:
            self._on_rotate(existing)
        return plaintext, existing

    def revoke(self, key_id: str) -> None:
        record = self._keys.get(key_id)
        if record is None:
            raise KeyError(f"unknown api key id: {key_id}")
        record.revoked = True
        if self._on_revoke is not None:
            self._on_revoke(record)

    def verify(self, key_id: str, plaintext: str) -> bool:
        record = self._keys.get(key_id)
        if record is None or record.revoked:
            return False
        return record.key_hash == self._hash(plaintext)

    @staticmethod
    def _hash(plaintext: str) -> str:
        return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
