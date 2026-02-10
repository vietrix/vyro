import asyncio

from vyro.middleware.base import Middleware
from vyro.middleware.chain import MiddlewareChain


class _SampleMiddleware:
    async def before_request(self, ctx):  # type: ignore[no-untyped-def]
        return None

    async def after_response(self, ctx, response):  # type: ignore[no-untyped-def]
        return response


def test_middleware_chain_constructs() -> None:
    chain = MiddlewareChain([_SampleMiddleware()])
    assert chain is not None


def test_middleware_chain_preserves_after_reverse_order() -> None:
    order: list[str] = []

    class _A(Middleware):
        async def before_request(self, ctx):  # type: ignore[no-untyped-def]
            order.append("before-a")

        async def after_response(self, ctx, response):  # type: ignore[no-untyped-def]
            order.append("after-a")
            return response

    class _B(Middleware):
        async def before_request(self, ctx):  # type: ignore[no-untyped-def]
            order.append("before-b")

        async def after_response(self, ctx, response):  # type: ignore[no-untyped-def]
            order.append("after-b")
            return response

    chain = MiddlewareChain([_A(), _B()])
    asyncio.run(chain.run_before({}))
    asyncio.run(chain.run_after({}, {"ok": True}))
    assert order == ["before-a", "before-b", "after-b", "after-a"]


def test_middleware_chain_skips_default_hooks() -> None:
    class _Noop(Middleware):
        pass

    chain = MiddlewareChain([_Noop()])
    asyncio.run(chain.run_before({}))
    response = asyncio.run(chain.run_after({}, {"ok": True}))
    assert response == {"ok": True}
