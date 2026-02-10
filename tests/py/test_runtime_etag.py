from __future__ import annotations

from vyro.runtime.edge.etag import ETagManager


def test_etag_manager_generates_stable_tag_for_same_payload() -> None:
    manager = ETagManager()
    first = manager.generate(b"hello")
    second = manager.generate(b"hello")
    assert first == second
    assert first.startswith("\"") and first.endswith("\"")


def test_etag_manager_detects_if_none_match_hit() -> None:
    manager = ETagManager()
    payload = b"resource"
    etag = manager.generate(payload)
    result = manager.evaluate(payload, if_none_match=etag)
    assert result.not_modified is True
    assert result.status == 304
    assert result.headers["etag"] == etag


def test_etag_manager_miss_keeps_200_status() -> None:
    manager = ETagManager()
    result = manager.evaluate(b"resource", if_none_match="\"other\"")
    assert result.not_modified is False
    assert result.status == 200
