from __future__ import annotations

import sqlite3
from pathlib import Path

from vyro.runtime.migrations import MigrationRunner


def test_migration_runner_applies_sql_files_once(tmp_path: Path) -> None:
    db = tmp_path / "app.db"
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_create_users.sql").write_text(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL);",
        encoding="utf-8",
    )

    runner = MigrationRunner(database=db, migrations_dir=migrations)
    first = runner.run()
    second = runner.run()

    assert first.applied == ["001_create_users.sql"]
    assert second.applied == []
    assert second.skipped == ["001_create_users.sql"]

    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchall()
        assert rows


def test_migration_runner_dry_run_does_not_apply(tmp_path: Path) -> None:
    db = tmp_path / "app.db"
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_create_logs.sql").write_text(
        "CREATE TABLE logs (id INTEGER PRIMARY KEY);",
        encoding="utf-8",
    )

    runner = MigrationRunner(database=db, migrations_dir=migrations)
    result = runner.run(dry_run=True)
    assert result.applied == []
    assert result.skipped == ["001_create_logs.sql"]
