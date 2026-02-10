from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(slots=True)
class CSRFProtector:
    secret: bytes
    header_name: str = "x-csrf-token"
    cookie_name: str = "vyro_csrf"

    @classmethod
    def with_random_secret(cls) -> CSRFProtector:
        return cls(secret=secrets.token_bytes(32))

    def issue_token(self, session_id: str) -> str:
        nonce = secrets.token_hex(16)
        sig = self._sign(session_id, nonce)
        return f"{nonce}.{sig}"

    def verify(self, session_id: str, token: str | None, *, method: str) -> bool:
        if method.upper() in {"GET", "HEAD", "OPTIONS", "TRACE"}:
            return True
        if not token or "." not in token:
            return False
        nonce, got_sig = token.split(".", 1)
        expected = self._sign(session_id, nonce)
        return hmac.compare_digest(got_sig, expected)

    def _sign(self, session_id: str, nonce: str) -> str:
        payload = f"{session_id}:{nonce}".encode("utf-8")
        digest = hmac.new(self.secret, payload, hashlib.sha256).hexdigest()
        return digest
