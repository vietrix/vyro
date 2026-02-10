from __future__ import annotations

from pathlib import Path

import pytest

from vyro.runtime.data.db_pool import DBConnectionPoolManager


def test_db_connection_pool_manager_register_and_get(tmp_path: Path) -> None:
    manager = DBConnectionPoolManager()
    pool = manager.register("main", database=tmp_path / "main.db", max_size=2)
    same = manager.get("main")
    assert same is pool


def test_db_connection_pool_acquire_release_and_limit(tmp_path: Path) -> None:
    manager = DBConnectionPoolManager()
    pool = manager.register("main", database=tmp_path / "main.db", max_size=1)
    conn = pool.acquire()
    assert conn is not None
    assert pool.in_use == 1
    with pytest.raises(RuntimeError, match="pool exhausted"):
        pool.acquire()
    pool.release()
    assert pool.in_use == 0


def test_db_connection_pool_manager_unknown_pool() -> None:
    manager = DBConnectionPoolManager()
    with pytest.raises(KeyError, match="unknown db pool"):
        manager.get("missing")
