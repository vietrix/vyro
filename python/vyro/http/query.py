from __future__ import annotations

from urllib.parse import parse_qsl


def parse_query_string(query: str | None) -> dict[str, str]:
    if not query:
        return {}
    return dict(parse_qsl(query, keep_blank_values=True))
