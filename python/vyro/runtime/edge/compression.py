from __future__ import annotations

import gzip
from dataclasses import dataclass
from typing import Literal
from zlib import compress as zlib_compress

CompressionProfile = Literal["speed", "balanced", "size"]


@dataclass(slots=True)
class ResponseCompressor:
    min_size: int = 256

    def compress(
        self,
        payload: bytes,
        *,
        accept_encoding: str | None,
        profile: CompressionProfile = "balanced",
    ) -> tuple[bytes, dict[str, str]]:
        if len(payload) < self.min_size:
            return payload, {}
        encoding = self._choose_encoding(accept_encoding)
        if encoding is None:
            return payload, {}

        if encoding == "gzip":
            level = self._gzip_level(profile)
            compressed = gzip.compress(payload, compresslevel=level)
        else:
            level = self._zlib_level(profile)
            compressed = zlib_compress(payload, level)

        headers = {"content-encoding": encoding, "vary": "accept-encoding"}
        return compressed, headers

    @staticmethod
    def _choose_encoding(accept_encoding: str | None) -> str | None:
        if not accept_encoding:
            return None
        normalized = accept_encoding.lower()
        if "gzip" in normalized:
            return "gzip"
        if "deflate" in normalized:
            return "deflate"
        return None

    @staticmethod
    def _gzip_level(profile: CompressionProfile) -> int:
        if profile == "speed":
            return 1
        if profile == "size":
            return 9
        return 6

    @staticmethod
    def _zlib_level(profile: CompressionProfile) -> int:
        if profile == "speed":
            return 1
        if profile == "size":
            return 9
        return 6
