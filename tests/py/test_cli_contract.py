import json
from pathlib import Path

from typer.testing import CliRunner

from vyro.cli.main import app
from vyro.cli.commands import core as core_cmd


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Vyro command line interface." in result.stdout
    assert "release" in result.stdout


def test_cli_version() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    record = json.loads(result.stdout.strip())
    assert record["level"] == "INFO"
    assert "vyro" in record["message"]


def test_cli_run_requires_valid_app_target() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "--app", "invalid-target"])
    assert result.exit_code == 2


def test_cli_migrate_dry_run() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        migrations = Path("migrations")
        migrations.mkdir()
        (migrations / "001_init.sql").write_text(
            "CREATE TABLE x (id INTEGER PRIMARY KEY);",
            encoding="utf-8",
        )
        result = runner.invoke(
            app,
            [
                "migrate",
                "--db",
                "app.db",
                "--dir",
                "migrations",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        record = json.loads(result.stdout.strip())
        assert record["level"] == "INFO"
        assert "Migration dry-run completed." in record["message"]


def test_cli_drift_reports_missing_schema(tmp_path) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    db = tmp_path / "app.db"
    schema = tmp_path / "schema.json"
    schema.write_text("{}", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "drift",
            "--db",
            str(db),
            "--schema",
            str(schema),
        ],
    )
    assert result.exit_code == 0
    record = json.loads(result.stdout.strip())
    assert record["level"] == "INFO"
    assert "Schema drift check passed." in record["message"]


def test_cli_doctor_strict_fails_when_secret_missing(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    monkeypatch.setattr(core_cmd.shutil, "which", lambda _: "/usr/bin/fake")
    monkeypatch.setattr(
        core_cmd.subprocess,
        "run",
        lambda *args, **kwargs: type("R", (), {"stdout": "rustc 1.80.0"})(),
    )

    result = runner.invoke(
        app,
        ["doctor", "--strict"],
        env={
            "VYRO_ENV": "production",
            "VYRO_WORKERS": "4",
            "VYRO_SECRET_KEY": "",
            "VYRO_LOG_SAMPLE_INFO": "1",
            "VYRO_LOG_SAMPLE_WARN": "1",
            "VYRO_LOG_SAMPLE_ERROR": "1",
        },
    )
    assert result.exit_code == 1


def test_cli_doctor_non_strict_emits_readiness_summary(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    monkeypatch.setattr(core_cmd.shutil, "which", lambda _: "/usr/bin/fake")
    monkeypatch.setattr(
        core_cmd.subprocess,
        "run",
        lambda *args, **kwargs: type("R", (), {"stdout": "rustc 1.80.0"})(),
    )

    result = runner.invoke(
        app,
        ["doctor", "--no-strict"],
        env={
            "VYRO_ENV": "production",
            "VYRO_SECRET_KEY": "x" * 24,
            "VYRO_WORKERS": "2",
            "VYRO_LOG_SAMPLE_INFO": "1",
            "VYRO_LOG_SAMPLE_WARN": "1",
            "VYRO_LOG_SAMPLE_ERROR": "1",
        },
    )
    assert result.exit_code == 0
