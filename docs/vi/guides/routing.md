# Định tuyến

## Path DSL

- `/users/:id` -> tham số có tên
- `/static/*` -> wildcard catch-all

## Versioning và deprecation

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## Lỗi

Signature không hợp lệ hoặc route mơ hồ sẽ raise `RouteDefinitionError` / `HandlerSignatureError`.
