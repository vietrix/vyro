from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class AsyncSQLAdapter(Protocol):
    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        ...

    async def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        ...


@dataclass(slots=True)
class SQLiteAsyncAdapter:
    database: Path

    def __post_init__(self) -> None:
        self.database = Path(self.database)

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        return await asyncio.to_thread(self._execute_sync, query, params)

    async def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._fetch_all_sync, query, params)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        return conn

    def _execute_sync(self, query: str, params: tuple[Any, ...]) -> int:
        with self._connect() as conn:
            cur = conn.execute(query, params)
            conn.commit()
            return cur.rowcount

    def _fetch_all_sync(self, query: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
