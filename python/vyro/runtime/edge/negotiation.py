from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NegotiationResult:
    media_type: str | None
    matched: bool


class ContentNegotiator:
    def choose(self, accept: str | None, available: list[str]) -> NegotiationResult:
        if not available:
            return NegotiationResult(media_type=None, matched=False)
        if not accept or accept.strip() == "*/*":
            return NegotiationResult(media_type=available[0], matched=True)

        ranked = self._parse_accept(accept)
        for candidate, _weight in ranked:
            for option in available:
                if self._matches(candidate, option):
                    return NegotiationResult(media_type=option, matched=True)
        return NegotiationResult(media_type=None, matched=False)

    @staticmethod
    def _parse_accept(accept: str) -> list[tuple[str, float]]:
        items: list[tuple[str, float]] = []
        for raw in accept.split(","):
            token = raw.strip()
            if not token:
                continue
            media_type = token
            q = 1.0
            if ";" in token:
                media_type, *params = [x.strip() for x in token.split(";")]
                for p in params:
                    if p.startswith("q="):
                        try:
                            q = float(p[2:])
                        except ValueError:
                            q = 0.0
            items.append((media_type, q))
        items.sort(key=lambda item: item[1], reverse=True)
        return items

    @staticmethod
    def _matches(candidate: str, offered: str) -> bool:
        if candidate == "*/*":
            return True
        if candidate.endswith("/*"):
            prefix = candidate.split("/", 1)[0]
            return offered.startswith(prefix + "/")
        return candidate == offered
