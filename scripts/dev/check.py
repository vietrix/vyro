from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from vyro.routing.lint import lint_project


def run() -> int:
    commands = [
        ["cargo", "fmt", "--all", "--", "--check"],
        ["cargo", "clippy", "--all-targets", "--", "-D", "warnings"],
        [sys.executable, "-m", "compileall", "-q", "python", "tests", "examples"],
    ]
    for command in commands:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode

    issues = lint_project(Path("."))
    if issues:
        for issue in issues:
            print(f"ERROR: {issue.path}:{issue.line} {issue.message}", file=sys.stderr)
        return 1
    print("INFO: route signature lint passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
