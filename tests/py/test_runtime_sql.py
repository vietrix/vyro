from __future__ import annotations

import asyncio
from pathlib import Path

from vyro.runtime.sql import SQLiteAsyncAdapter


def test_sqlite_async_adapter_execute_and_fetch_all(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    adapter = SQLiteAsyncAdapter(database=db_path)

    async def run() -> None:
        await adapter.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        await adapter.execute(
            "INSERT INTO users (name) VALUES (?)",
            ("alice",),
        )
        rows = await adapter.fetch_all("SELECT id, name FROM users")
        assert len(rows) == 1
        assert rows[0]["name"] == "alice"

    asyncio.run(run())
