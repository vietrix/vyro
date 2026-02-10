import inspect
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

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


def test_bind_request_kwargs_advanced_scalar_coercion() -> None:
    def handler(
        ctx,
        uid: UUID,
        created_at: datetime,
        due: date,
        price: Decimal,
        retries: Optional[int],
    ):  # type: ignore[no-untyped-def]
        return uid, created_at, due, price, retries

    params = list(inspect.signature(handler).parameters.values())
    kwargs = bind_request_kwargs(
        "handler",
        params,
        {},
        {
            "uid": "0f8fad5b-d9cb-469f-a165-70867728950e",
            "created_at": "2026-02-10T11:22:33",
            "due": "2026-02-15",
            "price": "19.99",
            "retries": "3",
        },
        {},
    )
    assert isinstance(kwargs["uid"], UUID)
    assert isinstance(kwargs["created_at"], datetime)
    assert isinstance(kwargs["due"], date)
    assert isinstance(kwargs["price"], Decimal)
    assert kwargs["retries"] == 3
