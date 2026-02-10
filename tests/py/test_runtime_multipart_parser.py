from __future__ import annotations

from vyro.runtime.edge.multipart_parser import MultipartParser


def test_multipart_parser_extracts_multiple_sections() -> None:
    parser = MultipartParser()
    boundary = b"xyz"
    payload = (
        b"--xyz\r\n"
        b"Content-Disposition: form-data; name=\"field1\"\r\n"
        b"\r\n"
        b"value1\r\n"
        b"--xyz\r\n"
        b"Content-Disposition: form-data; name=\"file\"; filename=\"a.txt\"\r\n"
        b"Content-Type: text/plain\r\n"
        b"\r\n"
        b"hello.txt\r\n"
        b"--xyz--\r\n"
    )
    sections = parser.parse(payload, boundary=boundary)
    assert len(sections) == 2
    assert sections[0].headers["content-disposition"].startswith("form-data; name=\"field1\"")
    assert sections[0].body == b"value1"
    assert sections[1].headers["content-type"] == "text/plain"
    assert sections[1].body == b"hello.txt"


def test_multipart_parser_returns_empty_when_boundary_not_found() -> None:
    parser = MultipartParser()
    sections = parser.parse(b"plain body", boundary=b"abc")
    assert sections == []
