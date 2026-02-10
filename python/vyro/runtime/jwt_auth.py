from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


@dataclass(slots=True)
class JWTAuthGuard:
    secret: bytes
    issuer: str = "vyro"
    audience: str = "vyro-api"

    def issue(self, subject: str, *, scopes: list[str] | None = None, ttl_seconds: int = 300) -> str:
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload: dict[str, Any] = {
            "sub": subject,
            "iss": self.issuer,
            "aud": self.audience,
            "iat": now,
            "exp": now + ttl_seconds,
            "scopes": scopes or [],
        }
        return self._encode(header, payload)

    def verify(self, token: str) -> dict[str, Any] | None:
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
        except ValueError:
            return None

        signed = f"{header_b64}.{payload_b64}".encode("ascii")
        expected = hmac.new(self.secret, signed, hashlib.sha256).digest()
        got = _b64url_decode(signature_b64)
        if not hmac.compare_digest(expected, got):
            return None

        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        now = int(time.time())
        if payload.get("iss") != self.issuer:
            return None
        if payload.get("aud") != self.audience:
            return None
        if int(payload.get("exp", 0)) <= now:
            return None
        return payload

    def authorize(self, token: str, required_scopes: set[str]) -> bool:
        payload = self.verify(token)
        if payload is None:
            return False
        granted = set(payload.get("scopes", []))
        return required_scopes.issubset(granted)

    def _encode(self, header: dict[str, Any], payload: dict[str, Any]) -> str:
        header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signed = f"{header_b64}.{payload_b64}".encode("ascii")
        signature = hmac.new(self.secret, signed, hashlib.sha256).digest()
        signature_b64 = _b64url_encode(signature)
        return f"{header_b64}.{payload_b64}.{signature_b64}"
