from __future__ import annotations

import pytest

from vyro.runtime.multipart_upload import MultipartUploadStream


def test_multipart_upload_stream_collects_chunks_and_detects_closing_boundary() -> None:
    stream = MultipartUploadStream(boundary=b"boundary")
    stream.feed(b"--boundary\r\ncontent\r\n")
    assert stream.has_complete_payload() is False
    stream.feed(b"--boundary--\r\n")
    assert stream.has_complete_payload() is True
    assert stream.size > 0


def test_multipart_upload_stream_enforces_max_size() -> None:
    stream = MultipartUploadStream(boundary=b"x", max_bytes=4)
    with pytest.raises(ValueError, match="exceeds max_bytes"):
        stream.feed(b"12345")


def test_multipart_upload_stream_rejects_feed_after_close() -> None:
    stream = MultipartUploadStream(boundary=b"x")
    stream.close()
    with pytest.raises(RuntimeError, match="already closed"):
        stream.feed(b"a")
