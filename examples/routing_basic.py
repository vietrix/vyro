from vyro import Context, Vyro

app = Vyro()


@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    return {"user_id": id, "query": dict(ctx.query)}


@app.get("/static/*")
async def static_file(ctx: Context, wildcard: str):
    return {"path": wildcard}


if __name__ == "__main__":
    app.run(port=8000, workers=2)
