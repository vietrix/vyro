from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Http2Stream:
    stream_id: int
    headers: dict[str, str] = field(default_factory=dict)
    _buffer: bytearray = field(default_factory=bytearray, repr=False)
    closed: bool = False

    def receive_data(self, chunk: bytes, *, end_stream: bool = False) -> None:
        if self.closed:
            raise RuntimeError("stream already closed")
        self._buffer.extend(chunk)
        if end_stream:
            self.closed = True

    def body(self) -> bytes:
        return bytes(self._buffer)


@dataclass(slots=True)
class Http2StreamManager:
    _next_id: int = 1
    _streams: dict[int, Http2Stream] = field(default_factory=dict)

    def open_stream(self, headers: dict[str, str] | None = None) -> Http2Stream:
        stream_id = self._next_id
        self._next_id += 2
        stream = Http2Stream(stream_id=stream_id, headers=headers or {})
        self._streams[stream_id] = stream
        return stream

    def get_stream(self, stream_id: int) -> Http2Stream | None:
        return self._streams.get(stream_id)

    def close_stream(self, stream_id: int) -> None:
        stream = self._streams.get(stream_id)
        if stream is None:
            return
        stream.closed = True
