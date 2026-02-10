from __future__ import annotations

import subprocess
import sys


def run() -> int:
    commands = [
        ["cargo", "test"],
        [sys.executable, "-m", "pytest", "tests/py", "tests/integration", "-q"],
    ]
    for command in commands:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
