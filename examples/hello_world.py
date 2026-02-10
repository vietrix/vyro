from vyro import Context, Vyro

app = Vyro()


@app.get("/")
async def hello(ctx: Context):
    return "Hello World"


if __name__ == "__main__":
    app.run(port=8000, workers=4)
