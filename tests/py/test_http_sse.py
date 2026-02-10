from __future__ import annotations

from vyro.http.sse import SSEEvent, SSEResponse


def test_sse_event_encode_includes_all_supported_fields() -> None:
    event = SSEEvent(
        data="line1\nline2",
        event="message",
        id="42",
        retry_ms=3000,
    )
    encoded = event.encode()
    assert "id: 42\n" in encoded
    assert "event: message\n" in encoded
    assert "retry: 3000\n" in encoded
    assert "data: line1\n" in encoded
    assert "data: line2\n\n" in encoded


def test_sse_response_builds_event_stream_payload_and_headers() -> None:
    stream = SSEResponse()
    stream.send("hello", event="tick", id="1")
    stream.send("world")

    body = stream.body_bytes().decode("utf-8")
    assert "event: tick\n" in body
    assert "id: 1\n" in body
    assert "data: hello\n\n" in body
    assert "data: world\n\n" in body

    payload, status, headers = stream.as_tuple()
    assert status == 200
    assert isinstance(payload, bytes)
    assert headers["content-type"].startswith("text/event-stream")
