from __future__ import annotations

from vyro.runtime.security.cors import CORSProfile


def test_cors_preset_standard_allows_origin_and_methods() -> None:
    profile = CORSProfile.preset("standard")
    headers = profile.apply(origin="https://example.com", preflight=True, request_method="GET")
    assert headers["access-control-allow-origin"] == "*"
    assert "GET" in headers["access-control-allow-methods"]
    assert headers["access-control-max-age"] == "600"


def test_cors_profile_rejects_disallowed_origin() -> None:
    profile = CORSProfile(name="strict", allow_origins=("https://trusted.example",))
    headers = profile.apply(origin="https://evil.example", preflight=False)
    assert headers == {}


def test_cors_preflight_rejects_disallowed_method() -> None:
    profile = CORSProfile(name="strict", allow_origins=("*",), allow_methods=("GET",))
    headers = profile.apply(origin="https://example.com", preflight=True, request_method="POST")
    assert headers == {}
