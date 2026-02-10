import pytest

from vyro import Vyro
from vyro.errors import HandlerSignatureError


def test_sync_handler_is_rejected() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError):

        @app.get("/users/:id")
        def sync_handler(ctx):  # type: ignore[no-untyped-def]
            return {"ok": True}


def test_app_symbol_is_removed() -> None:
    with pytest.raises(ImportError):
        from vyro import App  # type: ignore[attr-defined]  # noqa: F401


def test_first_param_must_be_ctx() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="first argument must be named 'ctx'"):

        @app.get("/users/:id")
        async def invalid(first, id: int):  # type: ignore[no-untyped-def]
            return {"id": id}


def test_handler_must_have_ctx_param() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="must accept first argument 'ctx'"):

        @app.get("/users/:id")
        async def invalid():  # type: ignore[no-untyped-def]
            return {"ok": True}
