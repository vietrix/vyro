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
