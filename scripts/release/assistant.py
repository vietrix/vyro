from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path

from .release import cmd_changelog, resolve_tag


def cmd_assistant(args: argparse.Namespace) -> int:
    tag = resolve_tag(args.tag)
    changelog_path = Path(args.changelog)
    notes_path = Path(args.out)
    dist_dir = Path(args.dist_dir)

    code = cmd_changelog(
        argparse.Namespace(
            tag=tag,
            changelog=str(changelog_path),
            out=str(notes_path),
        )
    )
    if code != 0:
        return code

    artifacts = _collect_artifacts(dist_dir)
    if not artifacts:
        raise FileNotFoundError(f"no distribution artifacts found in '{dist_dir}'")

    commands: list[list[str]] = []
    if args.publish_pypi:
        commands.append(["python", "-m", "twine", "upload", *artifacts])
    if args.publish_github:
        prerelease = "true" if "-rc." in tag else "false"
        commands.append(
            [
                "gh",
                "release",
                "create",
                tag,
                *artifacts,
                str(notes_path),
                str(changelog_path),
                "--notes-file",
                str(notes_path),
                "--prerelease",
                prerelease,
            ]
        )

    for command in commands:
        rendered = " ".join(shlex.quote(part) for part in command)
        print(f"Planned: {rendered}")
        if args.execute:
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                raise RuntimeError(f"command failed with code {result.returncode}: {rendered}")

    print(
        "Release assistant completed "
        f"(tag={tag}, artifacts={len(artifacts)}, execute={'yes' if args.execute else 'no'})."
    )
    return 0


def _collect_artifacts(dist_dir: Path) -> list[str]:
    wheels = sorted(str(path) for path in dist_dir.glob("*.whl"))
    sdists = sorted(str(path) for path in dist_dir.glob("*.tar.gz"))
    return [*wheels, *sdists]
