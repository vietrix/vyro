from __future__ import annotations

import pytest

from vyro.runtime.http2 import Http2StreamManager


def test_http2_stream_manager_opens_odd_stream_ids() -> None:
    manager = Http2StreamManager()
    first = manager.open_stream({":path": "/health"})
    second = manager.open_stream({":path": "/users"})
    assert first.stream_id == 1
    assert second.stream_id == 3


def test_http2_stream_accumulates_payload_until_closed() -> None:
    manager = Http2StreamManager()
    stream = manager.open_stream()
    stream.receive_data(b"hello ")
    stream.receive_data(b"world", end_stream=True)
    assert stream.body() == b"hello world"
    assert stream.closed is True
    with pytest.raises(RuntimeError, match="stream already closed"):
        stream.receive_data(b"!")


def test_http2_stream_manager_close_is_idempotent() -> None:
    manager = Http2StreamManager()
    stream = manager.open_stream()
    manager.close_stream(stream.stream_id)
    manager.close_stream(stream.stream_id)
    assert stream.closed is True
