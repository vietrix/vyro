from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DriftIssue:
    table: str
    message: str


@dataclass(slots=True)
class DriftReport:
    issues: list[DriftIssue] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return len(self.issues) > 0


@dataclass(slots=True)
class SchemaDriftDetector:
    database: Path

    def detect(self, expected_schema: dict[str, list[str]]) -> DriftReport:
        actual = self._read_actual_schema()
        issues: list[DriftIssue] = []

        for table, expected_columns in expected_schema.items():
            if table not in actual:
                issues.append(DriftIssue(table=table, message="table missing"))
                continue
            actual_columns = set(actual[table])
            for column in expected_columns:
                if column not in actual_columns:
                    issues.append(DriftIssue(table=table, message=f"column missing: {column}"))
            for extra in sorted(actual_columns - set(expected_columns)):
                issues.append(DriftIssue(table=table, message=f"unexpected column: {extra}"))

        for table in sorted(set(actual) - set(expected_schema)):
            issues.append(DriftIssue(table=table, message="unexpected table"))

        return DriftReport(issues=issues)

    def detect_from_file(self, schema_path: Path) -> DriftReport:
        raw = json.loads(schema_path.read_text(encoding="utf-8"))
        normalized = {str(k): [str(c) for c in v] for k, v in raw.items()}
        return self.detect(normalized)

    def _read_actual_schema(self) -> dict[str, list[str]]:
        with sqlite3.connect(self.database) as conn:
            tables = [
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ).fetchall()
            ]
            result: dict[str, list[str]] = {}
            for table in tables:
                cols = [row[1] for row in conn.execute(f"PRAGMA table_info('{table}')").fetchall()]
                result[table] = cols
            return result
