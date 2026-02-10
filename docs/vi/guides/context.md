# Context và Request/Response

`Context` cho phép truy cập metadata của request:

- `ctx.headers`
- `ctx.query`
- `ctx.path_params`
- `ctx.body_bytes()`

Ví dụ:

```python
@app.post("/events")
async def create_event(ctx: Context):
    ua = ctx.headers.get("user-agent", "unknown")
    size = len(ctx.body_bytes())
    return {"received": size, "ua": ua}
```
