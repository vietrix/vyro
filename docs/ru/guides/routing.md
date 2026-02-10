# Маршрутизация

## Путь DSL

- `/users/:id` -> именованный параметр
- `/static/*` -> всеобъемлющий

## Версии и устаревание

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## Ошибки

Неверные подписи или неоднозначные маршруты вызывают `RouteDefinitionError`/`HandlerSignatureError`.