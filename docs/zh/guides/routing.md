# 路由

## 路径 DSL

- `/users/:id` -> 命名参数
- `/static/*` -> 包罗万象

## 版本控制和弃用

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## 错误

无效签名或不明确的路由会引发 `RouteDefinitionError` / `HandlerSignatureError`。