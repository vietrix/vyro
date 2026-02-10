import argparse
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.release import assistant as release_assistant
from scripts.release import release as release_script
from scripts.release.versioning import parse_tag


def test_parse_release_tag_formats() -> None:
    stable = parse_tag("v1.2.3")
    rc = parse_tag("v1.2.3-rc.1")
    assert stable.python_version == "1.2.3"
    assert rc.python_version == "1.2.3rc1"


def test_resolve_tag_from_env(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("GITHUB_REF_NAME", "v9.9.9")
    assert release_script.resolve_tag(None) == "v9.9.9"


def test_resolve_tag_raises_without_input(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("GITHUB_REF_NAME", raising=False)
    with pytest.raises(ValueError, match="tag is required"):
        release_script.resolve_tag(None)


def test_cmd_changelog_updates_file(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    changelog = tmp_path / "CHANGELOG.md"
    notes = tmp_path / "release_notes.md"

    monkeypatch.setattr(release_script, "_build_markdown", lambda tag, include_github_notes: f"## {tag}\n\n- sample\n")
    args = argparse.Namespace(tag="v1.2.3", changelog=str(changelog), out=str(notes))

    code = release_script.cmd_changelog(args)
    assert code == 0
    assert "v1.2.3" in changelog.read_text(encoding="utf-8")
    assert notes.exists()


def test_cmd_assistant_dry_run_success(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "vyro-0.1.0-py3-none-any.whl").write_text("wheel", encoding="utf-8")
    (dist / "vyro-0.1.0.tar.gz").write_text("sdist", encoding="utf-8")

    changelog = tmp_path / "CHANGELOG.md"
    notes = tmp_path / "release_notes.md"

    def fake_cmd_changelog(_args):  # type: ignore[no-untyped-def]
        changelog.write_text("# Changelog\n", encoding="utf-8")
        notes.write_text("notes", encoding="utf-8")
        return 0

    monkeypatch.setattr(release_assistant, "cmd_changelog", fake_cmd_changelog)
    args = argparse.Namespace(
        tag="v1.2.3",
        dist_dir=str(dist),
        changelog=str(changelog),
        out=str(notes),
        publish_pypi=True,
        publish_github=True,
        execute=False,
    )
    code = release_assistant.cmd_assistant(args)
    assert code == 0


def test_cmd_assistant_fails_without_artifacts(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    dist = tmp_path / "dist"
    dist.mkdir()
    changelog = tmp_path / "CHANGELOG.md"
    notes = tmp_path / "release_notes.md"

    monkeypatch.setattr(release_assistant, "cmd_changelog", lambda _args: 0)
    args = argparse.Namespace(
        tag="v1.2.3",
        dist_dir=str(dist),
        changelog=str(changelog),
        out=str(notes),
        publish_pypi=True,
        publish_github=False,
        execute=False,
    )
    with pytest.raises(FileNotFoundError, match="no distribution artifacts"):
        release_assistant.cmd_assistant(args)
