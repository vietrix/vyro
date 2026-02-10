from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer

from vyro.openapi_compat import compare_openapi, load_openapi_document
from vyro.openapi import OpenAPIMeta, build_openapi_document, write_openapi_document
from vyro.runtime.kubernetes import KubernetesAppConfig, KubernetesManifestGenerator
from vyro.runtime.migrations import MigrationRunner
from vyro.runtime.nogil import NoGILWorkerTuner
from vyro.runtime.schema_drift import SchemaDriftDetector
from vyro.cli.runtime import (
    error,
    get_version_string,
    info,
    load_vyro_app,
    python_executable,
    require_module,
    warn,
)

app = typer.Typer(help="Core runtime commands for application users.")


@app.command("new")
def new_project(
    name: str = typer.Argument(..., help="Project directory name."),
    template: str = typer.Option(
        "minimal",
        "--template",
        help="Project template: minimal|service|hexagonal",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite existing app.py if present."),
) -> None:
    project_dir = Path(name)
    project_dir.mkdir(parents=True, exist_ok=True)
    package_name = _to_package_name(name)

    if template == "minimal":
        _scaffold_minimal(project_dir, force=force)
    elif template == "service":
        _scaffold_service(project_dir, package_name=package_name, force=force)
    elif template == "hexagonal":
        _scaffold_hexagonal(project_dir, package_name=package_name, force=force)
    else:
        typer.echo("ERROR: --template must be one of minimal|service|hexagonal", err=True)
        raise typer.Exit(code=2)

    info(f"Created '{template}' scaffold in '{project_dir}'.")


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


@app.command("k8s")
def k8s_generate(
    name: str = typer.Option(..., "--name", help="Application name."),
    image: str = typer.Option(..., "--image", help="Container image."),
    namespace: str = typer.Option("default", "--namespace"),
    replicas: int = typer.Option(2, "--replicas"),
    container_port: int = typer.Option(8000, "--container-port"),
    service_port: int = typer.Option(80, "--service-port"),
    workers: int = typer.Option(2, "--workers"),
    env: str = typer.Option("", "--env", help="Comma-separated KEY=VALUE pairs."),
    out: Path = typer.Option(Path("k8s.yaml"), "--out", help="Output manifest path."),
) -> None:
    if replicas < 1:
        typer.echo("ERROR: --replicas must be >= 1", err=True)
        raise typer.Exit(code=2)
    env_map = _parse_env_pairs(env)
    generator = KubernetesManifestGenerator()
    manifest = generator.generate(
        KubernetesAppConfig(
            name=name,
            image=image,
            namespace=namespace,
            replicas=replicas,
            container_port=container_port,
            service_port=service_port,
            workers=workers,
            env=env_map,
        )
    )
    out.write_text(manifest, encoding="utf-8")
    info(f"Kubernetes manifest generated at '{out}'.")


@app.command("nogil-tune")
def nogil_tune(
    workload: str = typer.Option("balanced", "--workload", help="Workload profile: cpu|io|balanced"),
    cpu_count: int = typer.Option(0, "--cpu-count", help="CPU count override (0 means auto-detect)."),
    out: Path | None = typer.Option(None, "--out", help="Optional JSON output file."),
) -> None:
    detected_cpu = cpu_count if cpu_count > 0 else (os.cpu_count() or 1)
    tuner = NoGILWorkerTuner()
    profile = tuner.recommend(cpu_count=detected_cpu, workload=workload)
    payload = profile.as_dict()
    info(
        "nogil tuning "
        f"mode={payload['mode']} cpu={payload['cpu_count']} workers={payload['workers']} "
        f"tokio_threads={payload['tokio_worker_threads']} python_threads={payload['python_threads']}"
    )
    if out is not None:
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        info(f"No-GIL tuning profile written to '{out}'.")


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


def _parse_env_pairs(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in raw.split(","):
        part = item.strip()
        if not part:
            continue
        key, sep, value = part.partition("=")
        if not sep:
            raise typer.BadParameter(f"invalid env pair '{part}', expected KEY=VALUE")
        k = key.strip()
        v = value.strip()
        if not k:
            raise typer.BadParameter(f"invalid env key in '{part}'")
        result[k] = v
    return result


def _to_package_name(raw: str) -> str:
    cleaned = raw.strip().replace("-", "_").replace(" ", "_")
    if not cleaned:
        return "app"
    if cleaned[0].isdigit():
        cleaned = f"app_{cleaned}"
    return "".join(ch for ch in cleaned if ch.isalnum() or ch == "_")


def _scaffold_minimal(project_dir: Path, *, force: bool) -> None:
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
    _ensure_readme(project_dir, "Minimal Vyro Project")


def _scaffold_service(project_dir: Path, *, package_name: str, force: bool) -> None:
    app_py = project_dir / "app.py"
    if app_py.exists() and not force:
        typer.echo("ERROR: app.py already exists. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)

    package_dir = project_dir / package_name
    api_dir = package_dir / "api"
    domain_dir = package_dir / "domain"
    infra_dir = package_dir / "infra"
    tests_dir = project_dir / "tests"
    for path in (package_dir, api_dir, domain_dir, infra_dir, tests_dir):
        path.mkdir(parents=True, exist_ok=True)

    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (api_dir / "__init__.py").write_text("", encoding="utf-8")
    (domain_dir / "__init__.py").write_text("", encoding="utf-8")
    (infra_dir / "__init__.py").write_text("", encoding="utf-8")

    app_py.write_text(
        "\n".join(
            [
                "from vyro import Vyro",
                f"from {package_name}.api.routes import register_routes",
                "",
                "app = Vyro()",
                "register_routes(app)",
                "",
                'if __name__ == "__main__":',
                "    app.run(port=8000, workers=2)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (api_dir / "routes.py").write_text(
        "\n".join(
            [
                "from vyro import Context, Vyro",
                "",
                "def register_routes(app: Vyro) -> None:",
                '    @app.get("/health")',
                "    async def health(ctx: Context):",
                '        return {"status": "ok"}',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (domain_dir / "services.py").write_text(
        "\n".join(
            [
                "class HealthService:",
                "    def status(self) -> str:",
                '        return "ok"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (infra_dir / "settings.py").write_text(
        "\n".join(
            [
                "HOST = '127.0.0.1'",
                "PORT = 8000",
                "WORKERS = 2",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (tests_dir / "test_health.py").write_text(
        "\n".join(
            [
                "def test_health_placeholder() -> None:",
                "    assert True",
                "",
            ]
        ),
        encoding="utf-8",
    )

    _ensure_readme(project_dir, "Service Template")


def _scaffold_hexagonal(project_dir: Path, *, package_name: str, force: bool) -> None:
    app_py = project_dir / "app.py"
    if app_py.exists() and not force:
        typer.echo("ERROR: app.py already exists. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)

    src_dir = project_dir / "src" / package_name
    app_dir = src_dir / "application"
    domain_dir = src_dir / "domain"
    ports_dir = src_dir / "ports"
    adapters_dir = src_dir / "adapters"
    for path in (src_dir, app_dir, domain_dir, ports_dir, adapters_dir):
        path.mkdir(parents=True, exist_ok=True)
        (path / "__init__.py").write_text("", encoding="utf-8")

    app_py.write_text(
        "\n".join(
            [
                "from vyro import Vyro, Context",
                "",
                "app = Vyro()",
                "",
                '@app.get("/health")',
                "async def health(ctx: Context):",
                '    return {"status": "ok", "architecture": "hexagonal"}',
                "",
                'if __name__ == "__main__":',
                "    app.run(port=8000, workers=2)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    _ensure_readme(project_dir, "Hexagonal Template")


def _ensure_readme(project_dir: Path, title: str) -> None:
    readme = project_dir / "README.md"
    if readme.exists():
        return
    readme.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                "Generated by `vyro new`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
