from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode


@dataclass(slots=True)
class OAuth2Config:
    issuer: str
    client_id: str
    client_secret: str
    authorize_endpoint: str
    token_endpoint: str
    redirect_uri: str
    scopes: tuple[str, ...] = ("openid", "profile", "email")


@dataclass(slots=True)
class OIDCClaims:
    subject: str
    email: str | None
    issuer: str
    audience: str


class OAuth2OIDCHelper:
    def __init__(self, config: OAuth2Config) -> None:
        self.config = config

    def build_authorize_url(self, *, state: str, nonce: str) -> str:
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.config.client_id,
                "redirect_uri": self.config.redirect_uri,
                "scope": " ".join(self.config.scopes),
                "state": state,
                "nonce": nonce,
            }
        )
        return f"{self.config.authorize_endpoint}?{query}"

    def build_token_request(self, *, code: str) -> dict[str, str]:
        return {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }

    def parse_id_token_claims(self, payload: dict[str, Any]) -> OIDCClaims:
        return OIDCClaims(
            subject=str(payload.get("sub", "")),
            email=payload.get("email"),
            issuer=str(payload.get("iss", "")),
            audience=str(payload.get("aud", "")),
        )


OAUTH2_DEFAULT_CONFIG = OAuth2Config(
    issuer="https://auth.example.local",
    client_id="vyro-dev-client",
    client_secret="vyro-dev-secret",
    authorize_endpoint="https://auth.example.local/oauth2/authorize",
    token_endpoint="https://auth.example.local/oauth2/token",
    redirect_uri="http://127.0.0.1:8000/callback",
)
