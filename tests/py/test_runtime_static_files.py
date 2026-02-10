from __future__ import annotations

from pathlib import Path

import pytest

from vyro.runtime.static_files import StaticFileService


def test_static_file_service_reads_file_inside_root(tmp_path: Path) -> None:
    root = tmp_path / "public"
    root.mkdir()
    target = root / "hello.txt"
    target.write_text("hello", encoding="utf-8")

    service = StaticFileService(root=root)
    assert service.read("/hello.txt") == b"hello"


def test_static_file_service_rejects_path_traversal(tmp_path: Path) -> None:
    root = tmp_path / "public"
    root.mkdir()
    service = StaticFileService(root=root)

    with pytest.raises(ValueError, match="escapes static root"):
        service.resolve("/../secret.txt")
