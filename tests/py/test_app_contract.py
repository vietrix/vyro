import pytest

from vyro.app import App
from vyro.errors import HandlerSignatureError


def test_sync_handler_is_rejected() -> None:
    app = App()

    with pytest.raises(HandlerSignatureError):

        @app.get("/users/:id")
        def sync_handler(ctx):  # type: ignore[no-untyped-def]
            return {"ok": True}
