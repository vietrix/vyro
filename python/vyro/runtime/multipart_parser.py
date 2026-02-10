from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MultipartSection:
    headers: dict[str, str]
    body: bytes


class MultipartParser:
    def parse(self, payload: bytes, *, boundary: bytes) -> list[MultipartSection]:
        marker = b"--" + boundary
        view = memoryview(payload)
        sections: list[MultipartSection] = []
        offset = 0

        while True:
            start = payload.find(marker, offset)
            if start < 0:
                break
            part_start = start + len(marker)

            if payload[part_start : part_start + 2] == b"--":
                break

            if payload[part_start : part_start + 2] == b"\r\n":
                part_start += 2

            header_end = payload.find(b"\r\n\r\n", part_start)
            if header_end < 0:
                break

            headers_blob = view[part_start:header_end].tobytes()
            body_start = header_end + 4
            next_marker = payload.find(b"\r\n" + marker, body_start)
            if next_marker < 0:
                break

            body = view[body_start:next_marker].tobytes()
            headers = self._parse_headers(headers_blob)
            sections.append(MultipartSection(headers=headers, body=body))
            offset = next_marker + 2

        return sections

    @staticmethod
    def _parse_headers(raw: bytes) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in raw.decode("utf-8").split("\r\n"):
            if not line or ":" not in line:
                continue
            name, value = line.split(":", 1)
            out[name.strip().lower()] = value.strip()
        return out
