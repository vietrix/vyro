import asyncio

from vyro.http.context import Context
from vyro.middleware.idempotency import IdempotencyKeyMiddleware


def _ctx(idempotency_key: str | None):
    headers = {}
    if idempotency_key is not None:
        headers["idempotency-key"] = idempotency_key
    return Context.from_native(
        {
            "headers": headers,
            "query": {},
            "path_params": {},
            "body": b"",
        }
    )


def test_idempotency_middleware_stores_first_response() -> None:
    mw = IdempotencyKeyMiddleware()
    ctx = _ctx("k-1")
    asyncio.run(mw.before_request(ctx))
    out = asyncio.run(mw.after_response(ctx, {"ok": True}))
    assert out == {"ok": True}
    assert mw.store.get("k-1") == {"ok": True}


def test_idempotency_middleware_replays_cached_response() -> None:
    mw = IdempotencyKeyMiddleware()
    first_ctx = _ctx("k-2")
    asyncio.run(mw.before_request(first_ctx))
    asyncio.run(mw.after_response(first_ctx, {"ok": "first"}))

    second_ctx = _ctx("k-2")
    asyncio.run(mw.before_request(second_ctx))
    out = asyncio.run(mw.after_response(second_ctx, {"ok": "second"}))
    assert out == {"ok": "first"}
