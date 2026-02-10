import inspect

import pytest

from vyro.errors import HandlerSignatureError
from vyro.routing.signature import bind_request_kwargs


def test_bind_request_kwargs_with_path_cast() -> None:
    def handler(ctx, id: int):  # type: ignore[no-untyped-def]
        return id

    params = list(inspect.signature(handler).parameters.values())
    kwargs = bind_request_kwargs("handler", params, {"id": "42"}, {}, {})
    assert kwargs["id"] == 42


def test_bind_request_kwargs_from_query_and_headers() -> None:
    def handler(ctx, limit: int, user_agent: str):  # type: ignore[no-untyped-def]
        return limit, user_agent

    params = list(inspect.signature(handler).parameters.values())
    kwargs = bind_request_kwargs(
        "handler",
        params,
        {},
        {"limit": "10"},
        {"User-Agent": "vyro-test"},
    )
    assert kwargs["limit"] == 10
    assert kwargs["user_agent"] == "vyro-test"


def test_bind_request_kwargs_missing_required_param() -> None:
    def handler(ctx, id: int):  # type: ignore[no-untyped-def]
        return id

    params = list(inspect.signature(handler).parameters.values())
    with pytest.raises(HandlerSignatureError, match="Missing request parameter 'id'"):
        bind_request_kwargs("handler", params, {}, {}, {})
