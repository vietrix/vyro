from __future__ import annotations

from dataclasses import dataclass
import re


TAG_PATTERN = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-rc\.(?P<rc>\d+))?$")


@dataclass(frozen=True)
class ParsedTag:
    raw: str
    major: int
    minor: int
    patch: int
    rc: int | None

    @property
    def prerelease(self) -> bool:
        return self.rc is not None

    @property
    def base_version(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def python_version(self) -> str:
        if self.rc is None:
            return self.base_version
        return f"{self.base_version}rc{self.rc}"


def parse_tag(tag: str) -> ParsedTag:
    match = TAG_PATTERN.match(tag)
    if not match:
        raise ValueError(
            f"Invalid tag '{tag}'. Expected format 'vX.Y.Z' or 'vX.Y.Z-rc.N'."
        )
    data = match.groupdict()
    rc_raw = data["rc"]
    return ParsedTag(
        raw=tag,
        major=int(data["major"]),
        minor=int(data["minor"]),
        patch=int(data["patch"]),
        rc=int(rc_raw) if rc_raw is not None else None,
    )

