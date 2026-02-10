# Context and Request/Response

`Context` gives access to request metadata:

- `ctx.headers`
- `ctx.query`
- `ctx.path_params`
- `ctx.body_bytes()`

Example:

```python
@app.post("/events")
async def create_event(ctx: Context):
    ua = ctx.headers.get("user-agent", "unknown")
    size = len(ctx.body_bytes())
    return {"received": size, "ua": ua}
```
