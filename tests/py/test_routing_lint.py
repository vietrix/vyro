from __future__ import annotations

from pathlib import Path

from vyro.routing.lint import lint_source


def test_lint_rejects_sync_route_handler() -> None:
    source = """
from vyro import Vyro
app = Vyro()

@app.get("/users/:id")
def handler(ctx, id: int):
    return {"id": id}
"""
    issues = lint_source(Path("example.py"), source)
    assert issues
    assert "must be declared with async def" in issues[0].message


def test_lint_rejects_missing_ctx_first_arg() -> None:
    source = """
from vyro import Vyro
app = Vyro()

@app.get("/users/:id")
async def handler(id: int):
    return {"id": id}
"""
    issues = lint_source(Path("example.py"), source)
    assert issues
    assert "first argument must be 'ctx'" in issues[0].message


def test_lint_accepts_valid_handler() -> None:
    source = """
from vyro import Vyro
app = Vyro()

@app.get("/users/:id")
async def handler(ctx, id: int):
    return {"id": id}
"""
    issues = lint_source(Path("example.py"), source)
    assert issues == []
