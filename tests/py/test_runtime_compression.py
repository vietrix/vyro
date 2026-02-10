from __future__ import annotations

import gzip
import zlib

from vyro.runtime.edge.compression import ResponseCompressor


def test_response_compressor_skips_small_payload() -> None:
    compressor = ResponseCompressor(min_size=10)
    payload = b"small"
    out, headers = compressor.compress(payload, accept_encoding="gzip")
    assert out == payload
    assert headers == {}


def test_response_compressor_uses_gzip_when_supported() -> None:
    compressor = ResponseCompressor(min_size=1)
    payload = b"hello world" * 20
    out, headers = compressor.compress(payload, accept_encoding="gzip, deflate", profile="balanced")
    assert headers["content-encoding"] == "gzip"
    assert headers["vary"] == "accept-encoding"
    assert gzip.decompress(out) == payload


def test_response_compressor_falls_back_to_deflate() -> None:
    compressor = ResponseCompressor(min_size=1)
    payload = b"hello world" * 20
    out, headers = compressor.compress(payload, accept_encoding="deflate", profile="speed")
    assert headers["content-encoding"] == "deflate"
    assert zlib.decompress(out) == payload
