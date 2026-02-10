from __future__ import annotations

import argparse
import subprocess


def run(sdist: bool) -> int:
    command = ["maturin", "build", "--release"]
    if sdist:
        command.append("--sdist")
    result = subprocess.run(command, check=False)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Developer build helper.")
    parser.add_argument("--sdist", action="store_true")
    args = parser.parse_args()
    return run(sdist=args.sdist)


if __name__ == "__main__":
    raise SystemExit(main())
