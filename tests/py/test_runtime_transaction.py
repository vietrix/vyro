from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.data.transaction import TransactionScope


class FakeAdapter:
    def __init__(self) -> None:
        self.commands: list[str] = []

    async def execute(self, query: str, params=()):  # type: ignore[no-untyped-def]
        self.commands.append(query)
        return 1


def test_transaction_scope_commits_on_success() -> None:
    scope = TransactionScope()
    db = FakeAdapter()

    @scope.transactional
    async def handler(ctx=None, db=None):  # type: ignore[no-untyped-def]
        return "ok"

    result = asyncio.run(handler(db=db))
    assert result == "ok"
    assert db.commands == ["BEGIN", "COMMIT"]


def test_transaction_scope_rolls_back_on_exception() -> None:
    scope = TransactionScope()
    db = FakeAdapter()

    @scope.transactional
    async def handler(ctx=None, db=None):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        asyncio.run(handler(db=db))
    assert db.commands == ["BEGIN", "ROLLBACK"]


def test_transaction_scope_skips_when_no_adapter_present() -> None:
    scope = TransactionScope()

    @scope.transactional
    async def handler(ctx=None):  # type: ignore[no-untyped-def]
        return 42

    assert asyncio.run(handler()) == 42
