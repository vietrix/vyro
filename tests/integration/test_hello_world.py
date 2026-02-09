from vyro import App, Context


def test_app_exposes_expected_api() -> None:
    app = App()

    @app.get("/")
    async def hello(ctx: Context):
        return "Hello World"

    assert hello is not None
