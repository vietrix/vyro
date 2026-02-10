from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer

from vyro.openapi_compat import compare_openapi, load_openapi_document
from vyro.openapi import OpenAPIMeta, build_openapi_document, write_openapi_document
from vyro.routing.lint import lint_project
from vyro.runtime.migrations import MigrationRunner
from vyro.runtime.schema_drift import SchemaDriftDetector
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
    issues = lint_project(Path("."))
    if issues:
        for issue in issues:
            typer.echo(f"ERROR: {issue.path}:{issue.line} {issue.message}", err=True)
        raise typer.Exit(code=1)
    info("Route signature lint passed.")


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


@app.command("migrate")
def migrate(
    db: Path = typer.Option(Path("app.db"), "--db", help="SQLite database path."),
    dir: Path = typer.Option(Path("migrations"), "--dir", help="Directory containing *.sql migrations."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show pending migrations without applying."),
) -> None:
    runner = MigrationRunner(database=db, migrations_dir=dir)
    result = runner.run(dry_run=dry_run)
    mode = "dry-run" if dry_run else "apply"
    info(
        f"Migration {mode} completed. applied={len(result.applied)} skipped={len(result.skipped)}"
    )


@app.command("drift")
def drift(
    db: Path = typer.Option(Path("app.db"), "--db", help="SQLite database path."),
    schema: Path = typer.Option(Path("schema.json"), "--schema", help="Expected schema JSON file."),
) -> None:
    detector = SchemaDriftDetector(database=db)
    report = detector.detect_from_file(schema)
    if report.has_drift:
        for issue in report.issues:
            typer.echo(f"ERROR: {issue.table} - {issue.message}", err=True)
        raise typer.Exit(code=1)
    info("Schema drift check passed.")


@app.command("version")
def version() -> None:
    info(f"vyro {get_version_string()}")


@app.command("doctor")
def doctor(
    production_readiness: bool = typer.Option(
        True,
        "--production-readiness/--no-production-readiness",
        help="Run production readiness checks.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict/--no-strict",
        help="Return non-zero when readiness checks report ERROR.",
    ),
) -> None:
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

    if not production_readiness:
        return

    readiness_errors = 0
    readiness_warnings = 0

    env_mode = os.getenv("VYRO_ENV", "").strip().lower()
    if env_mode == "production":
        info("readiness: VYRO_ENV=production")
    else:
        warn("readiness: VYRO_ENV should be 'production' for deploy targets")
        readiness_warnings += 1

    secret_key = os.getenv("VYRO_SECRET_KEY", "")
    if len(secret_key) >= 16:
        info("readiness: VYRO_SECRET_KEY is configured")
    else:
        error("readiness: VYRO_SECRET_KEY must be set and at least 16 chars")
        readiness_errors += 1

    workers_raw = os.getenv("VYRO_WORKERS", "")
    if workers_raw:
        try:
            workers = int(workers_raw)
            if workers >= 1:
                info(f"readiness: VYRO_WORKERS={workers}")
            else:
                warn("readiness: VYRO_WORKERS should be >= 1")
                readiness_warnings += 1
        except ValueError:
            warn("readiness: VYRO_WORKERS should be an integer")
            readiness_warnings += 1
    else:
        warn("readiness: VYRO_WORKERS is not set")
        readiness_warnings += 1

    if Path(".github/workflows/release.yml").exists():
        info("readiness: release workflow detected")
    else:
        warn("readiness: .github/workflows/release.yml not found")
        readiness_warnings += 1

    info(f"readiness-summary: errors={readiness_errors} warnings={readiness_warnings}")
    if strict and readiness_errors > 0:
        raise typer.Exit(code=1)


@app.command("openapi")
def openapi(
    app_target: str = typer.Option(..., "--app", help="Application target in format <module>:<attribute>."),
    out: Path = typer.Option(Path("openapi.json"), "--out", help="Output OpenAPI document path."),
    title: str = typer.Option("Vyro API", "--title"),
    version: str = typer.Option("0.1.0", "--version"),
) -> None:
    vyro_app = load_vyro_app(app_target)
    routes = vyro_app._router.records()  # noqa: SLF001
    doc = build_openapi_document(routes, OpenAPIMeta(title=title, version=version))
    write_openapi_document(out, doc)
    info(f"Wrote OpenAPI document to '{out}'.")


@app.command("compat")
def compat(
    base: Path = typer.Option(..., "--base", help="Base OpenAPI document path."),
    target: Path = typer.Option(..., "--target", help="Target OpenAPI document path."),
) -> None:
    base_doc = load_openapi_document(base)
    target_doc = load_openapi_document(target)
    issues = compare_openapi(base_doc, target_doc)
    if issues:
        for issue in issues:
            typer.echo(
                f"ERROR: {issue.method.upper()} {issue.path} - {issue.message}",
                err=True,
            )
        raise typer.Exit(code=1)
    info("OpenAPI compatibility check passed.")
