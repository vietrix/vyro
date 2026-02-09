from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
import subprocess
from typing import Iterable


CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\([^)]+\))?(?P<breaking>!)?:\s(?P<description>.+)$"
)

SECTION_MAP = {
    "feat": "Features",
    "fix": "Fixes",
    "perf": "Performance",
    "refactor": "Refactor",
    "docs": "Docs",
}

ORDER = ["Features", "Fixes", "Performance", "Refactor", "Docs", "Breaking", "Chores"]


@dataclass(frozen=True)
class CommitEntry:
    sha: str
    subject: str
    body: str


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    return result.stdout.strip()


def get_previous_tag(current_tag: str) -> str | None:
    output = _run_git(["tag", "--sort=version:refname"])
    tags = [t.strip() for t in output.splitlines() if t.strip()]
    if current_tag not in tags:
        return None
    idx = tags.index(current_tag)
    if idx == 0:
        return None
    return tags[idx - 1]


def load_commits(current_tag: str, previous_tag: str | None) -> list[CommitEntry]:
    rev_range = current_tag if previous_tag is None else f"{previous_tag}..{current_tag}"
    output = _run_git(["log", "--pretty=format:%H%x1f%s%x1f%b%x1e", rev_range])
    commits: list[CommitEntry] = []
    for chunk in output.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split("\x1f")
        if len(parts) < 3:
            continue
        sha, subject, body = parts[0], parts[1], parts[2]
        commits.append(CommitEntry(sha=sha, subject=subject.strip(), body=body.strip()))
    return commits


def classify_commit(commit: CommitEntry) -> tuple[str, str]:
    match = CONVENTIONAL_RE.match(commit.subject)
    if not match:
        return "Chores", commit.subject

    commit_type = match.group("type")
    description = match.group("description").strip()
    has_breaking = bool(match.group("breaking")) or "BREAKING CHANGE:" in commit.body
    if has_breaking:
        return "Breaking", description
    return SECTION_MAP.get(commit_type, "Chores"), description


def generate_release_markdown(tag: str, commits: Iterable[CommitEntry]) -> str:
    buckets: dict[str, list[str]] = {key: [] for key in ORDER}
    for commit in commits:
        section, description = classify_commit(commit)
        buckets[section].append(f"- {description} (`{commit.sha[:7]}`)")

    lines = [f"## {tag} - {date.today().isoformat()}", ""]
    emitted = False
    for section in ORDER:
        entries = buckets[section]
        if not entries:
            continue
        emitted = True
        lines.append(f"### {section}")
        lines.extend(entries)
        lines.append("")

    if not emitted:
        lines.append("### Chores")
        lines.append("- No user-facing changes.")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def prepend_changelog(changelog_path: str, new_block: str) -> None:
    try:
        with open(changelog_path, "r", encoding="utf-8") as fh:
            current = fh.read().strip()
    except FileNotFoundError:
        current = "# Changelog"

    if new_block.strip() in current:
        return

    if not current.startswith("# Changelog"):
        current = "# Changelog\n\n" + current

    head = "# Changelog\n\n"
    body = current[len(head) :].strip() if current.startswith(head) else current
    updated = f"{head}{new_block.strip()}\n\n{body}\n".strip() + "\n"
    with open(changelog_path, "w", encoding="utf-8") as fh:
        fh.write(updated)

