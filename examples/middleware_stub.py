from vyro import Context, Vyro
from vyro.middleware import Middleware

app = Vyro()


class LoggingMiddleware(Middleware):
    async def before_request(self, ctx):  # type: ignore[no-untyped-def]
        return None


app.add_middleware(LoggingMiddleware())


@app.get("/")
async def home(ctx: Context):
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(port=8011, workers=1)
