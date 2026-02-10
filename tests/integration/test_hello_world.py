from vyro import Context, Vyro


def test_app_exposes_expected_api() -> None:
    app = Vyro()

    @app.get("/")
    async def hello(ctx: Context):
        return "Hello World"

    assert hello is not None
