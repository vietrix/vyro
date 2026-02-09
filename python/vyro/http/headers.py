from __future__ import annotations

from typing import Mapping


def normalize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {k.lower(): v for k, v in headers.items()}
