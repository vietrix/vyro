from __future__ import annotations

import argparse

import typer

from vyro.cli.runtime import error, info

app = typer.Typer(help="Release automation commands.")


@app.command("notes")
def notes(
    tag: str = typer.Option(..., "--tag", help="Tag in format vX.Y.Z or vX.Y.Z-rc.N."),
    out: str = typer.Option(..., "--out", help="Output markdown file."),
    update_changelog: str | None = typer.Option(
        None,
        "--update-changelog",
        help="Optional CHANGELOG.md path for prepending generated notes.",
    ),
) -> None:
    try:
        from scripts.release.release import cmd_notes
    except Exception as exc:
        error(f"Cannot import release scripts: {exc}")
        raise typer.Exit(code=1) from exc

    namespace = argparse.Namespace(tag=tag, out=out, update_changelog=update_changelog)
    exit_code = cmd_notes(namespace)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)
    info(f"Release notes generated at '{out}'.")
