import json

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
