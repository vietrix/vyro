from __future__ import annotations

from vyro.runtime.oauth2_oidc import OAuth2Config, OAuth2OIDCHelper


def test_oauth2_oidc_helper_builds_authorize_url() -> None:
    helper = OAuth2OIDCHelper(
        OAuth2Config(
            issuer="https://auth.example.com",
            client_id="cid",
            client_secret="sec",
            authorize_endpoint="https://auth.example.com/authorize",
            token_endpoint="https://auth.example.com/token",
            redirect_uri="https://app.example.com/callback",
        )
    )
    url = helper.build_authorize_url(state="abc", nonce="n1")
    assert "response_type=code" in url
    assert "client_id=cid" in url
    assert "state=abc" in url
    assert "nonce=n1" in url


def test_oauth2_oidc_helper_builds_token_request_payload() -> None:
    helper = OAuth2OIDCHelper(
        OAuth2Config(
            issuer="https://auth.example.com",
            client_id="cid",
            client_secret="sec",
            authorize_endpoint="https://auth.example.com/authorize",
            token_endpoint="https://auth.example.com/token",
            redirect_uri="https://app.example.com/callback",
        )
    )
    payload = helper.build_token_request(code="code123")
    assert payload["grant_type"] == "authorization_code"
    assert payload["code"] == "code123"
    assert payload["client_id"] == "cid"


def test_oauth2_oidc_helper_parses_claims() -> None:
    helper = OAuth2OIDCHelper(
        OAuth2Config(
            issuer="https://auth.example.com",
            client_id="cid",
            client_secret="sec",
            authorize_endpoint="https://auth.example.com/authorize",
            token_endpoint="https://auth.example.com/token",
            redirect_uri="https://app.example.com/callback",
        )
    )
    claims = helper.parse_id_token_claims(
        {"sub": "u1", "email": "u1@example.com", "iss": "https://auth.example.com", "aud": "cid"}
    )
    assert claims.subject == "u1"
    assert claims.email == "u1@example.com"
