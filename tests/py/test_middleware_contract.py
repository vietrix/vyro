from vyro.middleware.chain import MiddlewareChain


class _SampleMiddleware:
    async def before_request(self, ctx):  # type: ignore[no-untyped-def]
        return None

    async def after_response(self, ctx, response):  # type: ignore[no-untyped-def]
        return response


def test_middleware_chain_constructs() -> None:
    chain = MiddlewareChain([_SampleMiddleware()])
    assert chain is not None
