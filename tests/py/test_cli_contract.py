import json
from pathlib import Path

from typer.testing import CliRunner

from vyro.cli.main import app


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
