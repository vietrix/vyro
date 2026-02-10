from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from vyro.runtime.schema_drift import SchemaDriftDetector


def _create_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()


def test_schema_drift_detector_reports_missing_and_unexpected_columns(tmp_path: Path) -> None:
    db = tmp_path / "app.db"
    _create_db(db)
    detector = SchemaDriftDetector(database=db)
    report = detector.detect({"users": ["id", "email"]})
    messages = [f"{issue.table}:{issue.message}" for issue in report.issues]
    assert "users:column missing: email" in messages
    assert "users:unexpected column: name" in messages


def test_schema_drift_detector_from_file(tmp_path: Path) -> None:
    db = tmp_path / "app.db"
    _create_db(db)
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps({"users": ["id", "name"]}), encoding="utf-8")
    detector = SchemaDriftDetector(database=db)
    report = detector.detect_from_file(schema_path)
    assert report.has_drift is False
