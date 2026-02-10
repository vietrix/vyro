from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .sql import SQLiteAsyncAdapter


@dataclass(slots=True)
class DBConnectionPool:
    database: Path
    max_size: int = 10
    _in_use: int = 0

    def acquire(self) -> SQLiteAsyncAdapter:
        if self._in_use >= self.max_size:
            raise RuntimeError("connection pool exhausted")
        self._in_use += 1
        return SQLiteAsyncAdapter(database=self.database)

    def release(self) -> None:
        if self._in_use > 0:
            self._in_use -= 1

    @property
    def in_use(self) -> int:
        return self._in_use


@dataclass(slots=True)
class DBConnectionPoolManager:
    _pools: dict[str, DBConnectionPool] = field(default_factory=dict)

    def register(self, name: str, *, database: Path, max_size: int = 10) -> DBConnectionPool:
        pool = DBConnectionPool(database=database, max_size=max_size)
        self._pools[name] = pool
        return pool

    def get(self, name: str) -> DBConnectionPool:
        if name not in self._pools:
            raise KeyError(f"unknown db pool: {name}")
        return self._pools[name]
