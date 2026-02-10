# 上下文和请求/响应

`Context` 提供对请求元数据的访问：

- ZXQ代码1ZXQ
- ZXQ代码2ZXQ
- ZXQ代码3ZXQ
- ZXQ代码4ZXQ

例子：

```python
@app.post("/events")
async def create_event(ctx: Context):
    ua = ctx.headers.get("user-agent", "unknown")
    size = len(ctx.body_bytes())
    return {"received": size, "ua": ua}
```
