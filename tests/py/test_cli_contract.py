import json
import sys
from pathlib import Path

from typer.testing import CliRunner

from vyro.cli.main import app
from vyro.cli.commands import core as core_cmd
from vyro.cli.runtime import load_vyro_app
from vyro.app.vyro import Vyro


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Vyro command line interface." in result.stdout
    assert "release" in result.stdout
    assert "workspace" in result.stdout


def test_cli_release_help_includes_changelog_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["release", "--help"])
    assert result.exit_code == 0
    assert "changelog" in result.stdout
    assert "assistant" in result.stdout


def test_cli_release_assistant_invokes_script(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    from scripts.release import assistant as assistant_module

    monkeypatch.setattr(assistant_module, "cmd_assistant", lambda _args: 0)
    result = runner.invoke(app, ["release", "assistant", "--no-publish-pypi", "--no-publish-github"])
    assert result.exit_code == 0


def test_cli_workspace_init_creates_monorepo_layout() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            ["workspace", "init", "platform", "--apps", "api,worker", "--libs", "common,events"],
        )
        assert result.exit_code == 0
        assert Path("platform/vyro.workspace.toml").exists()
        assert Path("platform/apps/api/app.py").exists()
        assert Path("platform/apps/worker/app.py").exists()
        assert Path("platform/libs/common/__init__.py").exists()
        assert Path("platform/libs/events/__init__.py").exists()


def test_cli_workspace_status_strict_fails_without_workspace_file() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["workspace", "status", "--strict"])
        assert result.exit_code == 1


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


def test_load_vyro_app_imports_module_from_current_working_directory(
    tmp_path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    app_module = tmp_path / "app.py"
    app_module.write_text(
        "from vyro import Vyro\n"
        "app = Vyro()\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry and entry != str(tmp_path)])
    sys.modules.pop("app", None)

    loaded = load_vyro_app("app:app")

    assert isinstance(loaded, Vyro)


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


def test_cli_help_hides_dev_toolchain_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert " check " not in result.stdout
    assert " test " not in result.stdout
    assert " build " not in result.stdout
    assert " bench " not in result.stdout


def test_cli_check_command_is_not_available() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["check"])
    assert result.exit_code != 0


def test_cli_k8s_generates_manifest(tmp_path) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    out_file = tmp_path / "k8s.yaml"
    result = runner.invoke(
        app,
        [
            "k8s",
            "--name",
            "vyro-api",
            "--image",
            "ghcr.io/vietrix/vyro:latest",
            "--namespace",
            "production",
            "--replicas",
            "2",
            "--env",
            "VYRO_ENV=production",
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    text = out_file.read_text(encoding="utf-8")
    assert "kind: Deployment" in text
    assert "kind: Service" in text


def test_cli_nogil_tune_writes_profile(tmp_path) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    out_file = tmp_path / "nogil.json"
    result = runner.invoke(
        app,
        [
            "nogil-tune",
            "--workload",
            "cpu",
            "--cpu-count",
            "8",
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["mode"] == "cpu"
    assert payload["workers"] == 8


def test_cli_new_service_template_scaffold() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["new", "inventory_service", "--template", "service"])
        assert result.exit_code == 0
        assert Path("inventory_service/app.py").exists()
        assert Path("inventory_service/inventory_service/api/routes.py").exists()
        assert Path("inventory_service/inventory_service/domain/services.py").exists()
        assert Path("inventory_service/tests/test_health.py").exists()


def test_cli_new_hexagonal_template_scaffold() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["new", "billing", "--template", "hexagonal"])
        assert result.exit_code == 0
        assert Path("billing/app.py").exists()
        assert Path("billing/src/billing/application/__init__.py").exists()
        assert Path("billing/src/billing/domain/__init__.py").exists()
        assert Path("billing/src/billing/ports/__init__.py").exists()
        assert Path("billing/src/billing/adapters/__init__.py").exists()


def test_cli_new_rejects_unknown_template() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["new", "demo", "--template", "unknown"])
        assert result.exit_code == 2
