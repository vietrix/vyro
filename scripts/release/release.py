from __future__ import annotations

import argparse
import sys

from .changelog import (
    generate_release_markdown,
    get_previous_tag,
    load_commits,
    prepend_changelog,
)
from .render import append_github_notes_block
from .versioning import parse_tag


def cmd_notes(args: argparse.Namespace) -> int:
    parsed = parse_tag(args.tag)
    previous_tag = get_previous_tag(parsed.raw)
    commits = load_commits(parsed.raw, previous_tag)
    markdown = append_github_notes_block(generate_release_markdown(parsed.raw, commits))

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    if args.update_changelog:
        prepend_changelog(args.update_changelog, markdown)

    print(f"Generated release notes: {args.out}")
    if args.update_changelog:
        print(f"Updated changelog: {args.update_changelog}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Release automation utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    notes = subparsers.add_parser("notes", help="Generate release notes markdown from git history.")
    notes.add_argument("--tag", required=True, help="Release tag in format vX.Y.Z or vX.Y.Z-rc.N")
    notes.add_argument("--out", required=True, help="Output markdown path")
    notes.add_argument(
        "--update-changelog",
        default=None,
        help="Optional CHANGELOG.md path to prepend generated notes block.",
    )
    notes.set_defaults(func=cmd_notes)

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
