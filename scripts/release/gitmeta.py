from __future__ import annotations

import subprocess


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def current_sha() -> str:
    return run_git(["rev-parse", "HEAD"])
