# コンテキストとリクエスト/レスポンス

`Context` は、リクエストのメタデータへのアクセスを許可します。

- `ctx.headers`
- `ctx.query`
- `ctx.path_params`
- ZXQコード4ZXQ

例：

```python
@app.post("/events")
async def create_event(ctx: Context):
    ua = ctx.headers.get("user-agent", "unknown")
    size = len(ctx.body_bytes())
    return {"received": size, "ua": ua}
```
