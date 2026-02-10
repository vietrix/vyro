from __future__ import annotations

from vyro.runtime.negotiation import ContentNegotiator


def test_content_negotiator_respects_q_weights() -> None:
    negotiator = ContentNegotiator()
    result = negotiator.choose(
        "application/json;q=0.5, text/plain;q=0.9",
        ["application/json", "text/plain"],
    )
    assert result.matched is True
    assert result.media_type == "text/plain"


def test_content_negotiator_supports_wildcards() -> None:
    negotiator = ContentNegotiator()
    result = negotiator.choose("application/*", ["text/plain", "application/json"])
    assert result.matched is True
    assert result.media_type == "application/json"


def test_content_negotiator_returns_no_match() -> None:
    negotiator = ContentNegotiator()
    result = negotiator.choose("image/png", ["application/json"])
    assert result.matched is False
    assert result.media_type is None
