from __future__ import annotations


def append_github_notes_block(base: str) -> str:
    footer = [
        "",
        "---",
        "",
        "### Auto Generated Notes",
        "The GitHub workflow appends generated release notes to this release.",
        "",
    ]
    return base.rstrip() + "\n" + "\n".join(footer)
