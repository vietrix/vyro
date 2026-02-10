from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .changelog import (
    generate_release_markdown,
    get_previous_tag,
    load_commits,
    prepend_changelog,
)
from .render import append_github_notes_block
from .versioning import parse_tag


def resolve_tag(tag: str | None) -> str:
    if tag and tag.strip():
        return tag.strip()
    env_tag = os.getenv("GITHUB_REF_NAME", "").strip()
    if env_tag:
        return env_tag
    raise ValueError("tag is required (use --tag or set GITHUB_REF_NAME)")


def _build_markdown(tag: str, *, include_github_notes: bool) -> str:
    parsed = parse_tag(tag)
    previous_tag = get_previous_tag(parsed.raw)
    commits = load_commits(parsed.raw, previous_tag)
    markdown = generate_release_markdown(parsed.raw, commits)
    if include_github_notes:
        return append_github_notes_block(markdown)
    return markdown


def cmd_notes(args: argparse.Namespace) -> int:
    tag = resolve_tag(args.tag)
    markdown = _build_markdown(tag, include_github_notes=True)

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    if args.update_changelog:
        prepend_changelog(args.update_changelog, markdown)

    print(f"Generated release notes: {args.out}")
    if args.update_changelog:
        print(f"Updated changelog: {args.update_changelog}")
    return 0


def cmd_changelog(args: argparse.Namespace) -> int:
    tag = resolve_tag(args.tag)
    markdown = _build_markdown(tag, include_github_notes=False)
    prepend_changelog(args.changelog, markdown)

    out = args.out
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(append_github_notes_block(markdown))
        print(f"Generated release notes: {out}")
    print(f"Updated changelog: {args.changelog}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Release automation utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    notes = subparsers.add_parser("notes", help="Generate release notes markdown from git history.")
    notes.add_argument("--tag", required=False, default=None, help="Release tag in format vX.Y.Z or vX.Y.Z-rc.N")
    notes.add_argument("--out", required=True, help="Output markdown path")
    notes.add_argument(
        "--update-changelog",
        default=None,
        help="Optional CHANGELOG.md path to prepend generated notes block.",
    )
    notes.set_defaults(func=cmd_notes)

    changelog = subparsers.add_parser(
        "changelog",
        help="Generate changelog block and prepend CHANGELOG.md (automated flow).",
    )
    changelog.add_argument("--tag", required=False, default=None, help="Release tag in format vX.Y.Z or vX.Y.Z-rc.N")
    changelog.add_argument(
        "--changelog",
        default=str(Path("CHANGELOG.md")),
        help="CHANGELOG.md path to prepend generated release block.",
    )
    changelog.add_argument(
        "--out",
        default=None,
        help="Optional output release_notes.md path with appended GitHub auto-generated block.",
    )
    changelog.set_defaults(func=cmd_changelog)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"release script error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
