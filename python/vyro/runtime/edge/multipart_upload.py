from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MultipartUploadStream:
    boundary: bytes
    max_bytes: int = 10 * 1024 * 1024
    _buffer: bytearray = field(default_factory=bytearray, repr=False)
    _closed: bool = False

    def feed(self, chunk: bytes) -> None:
        if self._closed:
            raise RuntimeError("multipart stream already closed")
        self._buffer.extend(chunk)
        if len(self._buffer) > self.max_bytes:
            raise ValueError("multipart payload exceeds max_bytes")

    def close(self) -> None:
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def size(self) -> int:
        return len(self._buffer)

    def raw_bytes(self) -> bytes:
        return bytes(self._buffer)

    def has_complete_payload(self) -> bool:
        closing_marker = b"--" + self.boundary + b"--"
        return closing_marker in self._buffer
