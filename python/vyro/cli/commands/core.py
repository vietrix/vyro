from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import typer

from vyro.cli.runtime import (
    get_version_string,
    info,
    load_vyro_app,
    python_executable,
    require_module,
    run_command,
    warn,
)

app = typer.Typer(help="Core development and runtime commands.")


@app.command("new")
def new_project(
    name: str = typer.Argument(..., help="Project directory name."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing app.py if present."),
) -> None:
    project_dir = Path(name)
    project_dir.mkdir(parents=True, exist_ok=True)

    app_py = project_dir / "app.py"
    if app_py.exists() and not force:
        typer.echo("ERROR: app.py already exists. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)

    app_py.write_text(
        "\n".join(
            [
                "from vyro import Vyro, Context",
                "",
                "app = Vyro()",
                "",
                '@app.get("/")',
                "async def hello(ctx: Context):",
                '    return {"message": "hello from vyro"}',
                "",
                'if __name__ == "__main__":',
                "    app.run(port=8000, workers=1)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    readme = project_dir / "README.md"
    if not readme.exists():
        readme.write_text("# New Vyro Project\n", encoding="utf-8")

    info(f"Created scaffold in '{project_dir}'.")


@app.command("run")
def run_server(
    app_target: str = typer.Option(..., "--app", help="Application target in format <module>:<attribute>."),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    workers: int = typer.Option(1, "--workers"),
) -> None:
    vyro_app = load_vyro_app(app_target)
    info(f"Starting Vyro app '{app_target}' on {host}:{port} with workers={workers}.")
    vyro_app.run(host=host, port=port, workers=workers)


@app.command("dev")
def dev_server(
    app_target: str = typer.Option(..., "--app", help="Application target in format <module>:<attribute>."),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    workers: int = typer.Option(1, "--workers"),
    reload: bool = typer.Option(True, "--reload/--no-reload"),
) -> None:
    if not reload:
        run_server(app_target=app_target, host=host, port=port, workers=workers)
        return

    if not require_module("watchfiles"):
        warn("watchfiles is not installed. Falling back to --no-reload mode.")
        run_server(app_target=app_target, host=host, port=port, workers=workers)
        return

    from watchfiles import run_process

    info("Starting dev server with autoreload.")
    run_process(
        ".",
        target=run_server,
        kwargs={"app_target": app_target, "host": host, "port": port, "workers": workers},
    )


@app.command("check")
def check() -> None:
    run_command(["cargo", "fmt", "--all", "--", "--check"])
    run_command(["cargo", "clippy", "--all-targets", "--", "-D", "warnings"])
    run_command([python_executable(), "-m", "compileall", "-q", "python", "tests", "examples"])


@app.command("test")
def test() -> None:
    run_command(["cargo", "test"])
    run_command([python_executable(), "-m", "pytest", "tests/py", "tests/integration", "-q"])


@app.command("build")
def build(
    sdist: bool = typer.Option(False, "--sdist", help="Build source distribution alongside wheels."),
) -> None:
    command = ["maturin", "build", "--release"]
    if sdist:
        command.append("--sdist")
    run_command(command)


@app.command("version")
def version() -> None:
    info(f"vyro {get_version_string()}")


@app.command("doctor")
def doctor() -> None:
    checks = {
        "python": python_executable(),
        "rustc": shutil.which("rustc") or "",
        "cargo": shutil.which("cargo") or "",
        "maturin": shutil.which("maturin") or "",
    }
    for tool, path in checks.items():
        if path:
            info(f"{tool}: {path}")
        else:
            typer.echo(f"ERROR: {tool} not found in PATH.", err=True)
            raise typer.Exit(code=1)

    info(f"python-version: {sys.version.split()[0]}")
    try:
        rust_version = subprocess.run(
            ["rustc", "--version"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        info(rust_version)
    except Exception:
        warn("Could not determine rustc version.")
