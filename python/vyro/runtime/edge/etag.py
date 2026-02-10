from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(slots=True)
class ETagEvaluation:
    etag: str
    not_modified: bool
    status: int
    headers: dict[str, str]


class ETagManager:
    @staticmethod
    def generate(payload: bytes, *, weak: bool = False) -> str:
        digest = hashlib.sha1(payload).hexdigest()
        value = f"\"{digest}\""
        if weak:
            return f"W/{value}"
        return value

    @staticmethod
    def is_not_modified(if_none_match: str | None, etag: str) -> bool:
        if not if_none_match:
            return False
        if if_none_match.strip() == "*":
            return True
        candidates = [part.strip() for part in if_none_match.split(",") if part.strip()]
        return etag in candidates

    def evaluate(self, payload: bytes, if_none_match: str | None) -> ETagEvaluation:
        etag = self.generate(payload)
        not_modified = self.is_not_modified(if_none_match, etag)
        status = 304 if not_modified else 200
        headers = {"etag": etag}
        return ETagEvaluation(etag=etag, not_modified=not_modified, status=status, headers=headers)
