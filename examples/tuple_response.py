from vyro import App, Context

app = App()


@app.get("/tuple")
async def tuple_response(ctx: Context):
    return ({"ok": True}, 201, {"x-powered-by": "vyro"})


if __name__ == "__main__":
    app.run(port=8010, workers=1)
