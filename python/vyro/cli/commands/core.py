from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
import sys
import time
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


@app.command("check")
def check(
    app_target: str | None = typer.Option(
        None,
        "--app",
        help="Application target in format <module>:<attribute> for API contract lint.",
    ),
    contract_base: Path = typer.Option(
        Path("openapi.contract.json"),
        "--contract-base",
        help="Baseline OpenAPI contract document path.",
    ),
    strict_contract: bool = typer.Option(
        True,
        "--strict-contract/--no-strict-contract",
        help="Fail when contract base is missing or compatibility issues are found.",
    ),
) -> None:
    run_command(["cargo", "fmt", "--all", "--", "--check"])
    run_command(["cargo", "clippy", "--all-targets", "--", "-D", "warnings"])
    run_command([python_executable(), "-m", "compileall", "-q", "python", "tests", "examples"])
    issues = lint_project(Path("."))
    if issues:
        for issue in issues:
            typer.echo(f"ERROR: {issue.path}:{issue.line} {issue.message}", err=True)
        raise typer.Exit(code=1)
    info("Route signature lint passed.")
    _run_api_contract_lint(
        app_target=app_target,
        contract_base=contract_base,
        strict_contract=strict_contract,
    )


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


@app.command("bench")
def bench(
    suite: str = typer.Option(
        "all",
        "--suite",
        help="Benchmark suite: routing|json|latency|all",
    ),
    iterations: int = typer.Option(10000, "--iterations", help="Iterations per benchmark."),
    out: Path | None = typer.Option(None, "--out", help="Optional JSON output file."),
) -> None:
    if iterations < 1:
        typer.echo("ERROR: --iterations must be >= 1", err=True)
        raise typer.Exit(code=2)

    selected = suite.strip().lower()
    allowed = {"routing", "json", "latency", "all"}
    if selected not in allowed:
        typer.echo("ERROR: --suite must be one of routing|json|latency|all", err=True)
        raise typer.Exit(code=2)

    benches = []
    if selected in {"routing", "all"}:
        benches.append(("routing", _bench_routing))
    if selected in {"json", "all"}:
        benches.append(("json", _bench_json))
    if selected in {"latency", "all"}:
        benches.append(("latency", _bench_latency))

    results: dict[str, dict[str, float | int]] = {}
    for name, fn in benches:
        duration_sec = fn(iterations)
        ops_per_sec = iterations / duration_sec if duration_sec > 0 else float("inf")
        us_per_op = (duration_sec * 1_000_000) / iterations
        results[name] = {
            "iterations": iterations,
            "duration_sec": round(duration_sec, 6),
            "ops_per_sec": round(ops_per_sec, 2),
            "us_per_op": round(us_per_op, 3),
        }
        info(
            f"bench[{name}] iterations={iterations} duration={duration_sec:.6f}s "
            f"ops_per_sec={ops_per_sec:.2f} us_per_op={us_per_op:.3f}"
        )

    if out is not None:
        payload = {
            "suite": selected,
            "results": results,
        }
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        info(f"Benchmark result written to '{out}'.")


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


def _run_api_contract_lint(
    *,
    app_target: str | None,
    contract_base: Path,
    strict_contract: bool,
) -> None:
    if app_target is None:
        info("API contract lint skipped (missing --app).")
        return

    if not contract_base.exists():
        message = f"API contract base file not found: {contract_base}"
        if strict_contract:
            typer.echo(f"ERROR: {message}", err=True)
            raise typer.Exit(code=1)
        warn(f"{message}. Skipping compatibility check.")
        return

    vyro_app = load_vyro_app(app_target)
    routes = vyro_app._router.records()  # noqa: SLF001
    current_doc = build_openapi_document(routes, OpenAPIMeta(title="Vyro API", version="current"))
    base_doc = load_openapi_document(contract_base)
    compat_issues = compare_openapi(base_doc, current_doc)
    if compat_issues:
        for issue in compat_issues:
            typer.echo(
                f"ERROR: API contract break {issue.method.upper()} {issue.path} - {issue.message}",
                err=True,
            )
        raise typer.Exit(code=1)
    info("API contract lint passed.")


def _bench_routing(iterations: int) -> float:
    from vyro.routing.normalize import normalize_path

    samples = ["/users/:id", "/static/*", "/v1/orders/:order_id/items/:item_id", "/health"]
    start = time.perf_counter()
    for i in range(iterations):
        normalize_path(samples[i % len(samples)])
    return time.perf_counter() - start


def _bench_json(iterations: int) -> float:
    payload = {"id": 1, "name": "vyro", "tags": ["rust", "python", "api"], "nested": {"ok": True}}
    start = time.perf_counter()
    for _ in range(iterations):
        encoded = json.dumps(payload, separators=(",", ":"))
        json.loads(encoded)
    return time.perf_counter() - start


def _bench_latency(iterations: int) -> float:
    samples: list[float] = []
    for i in range(iterations):
        t0 = time.perf_counter_ns()
        _ = (i * 3) ^ (i >> 1)
        t1 = time.perf_counter_ns()
        samples.append(float(t1 - t0))
    mean_ns = statistics.fmean(samples) if samples else 0.0
    total_sec = (mean_ns * iterations) / 1_000_000_000
    return total_sec


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
