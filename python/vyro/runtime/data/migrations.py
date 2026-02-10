from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MigrationResult:
    applied: list[str]
    skipped: list[str]


@dataclass(slots=True)
class MigrationRunner:
    database: Path
    migrations_dir: Path

    def run(self, *, dry_run: bool = False) -> MigrationResult:
        files = sorted(path for path in self.migrations_dir.glob("*.sql") if path.is_file())
        if dry_run:
            return MigrationResult(applied=[], skipped=[f.name for f in files])

        with sqlite3.connect(self.database) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS _vyro_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            existing = {
                row[0]
                for row in conn.execute("SELECT version FROM _vyro_migrations").fetchall()
            }

            applied: list[str] = []
            skipped: list[str] = []
            for file in files:
                version = file.name
                if version in existing:
                    skipped.append(version)
                    continue
                sql = file.read_text(encoding="utf-8")
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO _vyro_migrations(version, applied_at) VALUES (?, datetime('now'))",
                    (version,),
                )
                applied.append(version)
            conn.commit()
            return MigrationResult(applied=applied, skipped=skipped)
