from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StaticFileService:
    root: Path

    def __post_init__(self) -> None:
        self.root = self.root.resolve()

    def resolve(self, request_path: str) -> Path:
        normalized = request_path.lstrip("/")
        candidate = (self.root / normalized).resolve()
        if self.root not in candidate.parents and candidate != self.root:
            raise ValueError("path escapes static root")
        return candidate

    def read(self, request_path: str) -> bytes:
        target = self.resolve(request_path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(str(target))
        return target.read_bytes()
