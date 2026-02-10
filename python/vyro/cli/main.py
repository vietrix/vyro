from __future__ import annotations

import typer

from vyro.cli.commands.core import app as core_app
from vyro.cli.commands.release import app as release_app

app = typer.Typer(help="Vyro command line interface.")
app.add_typer(core_app)
app.add_typer(release_app, name="release")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
