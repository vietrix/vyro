# Routing

## Path DSL

- `/users/:id` -> named param
- `/static/*` -> catch-all

## Versioning and deprecation

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## Errors

Invalid signatures or ambiguous routes raise `RouteDefinitionError` / `HandlerSignatureError`.
