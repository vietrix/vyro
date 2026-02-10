# 컨텍스트 및 요청/응답

`Context`는 요청 메타데이터에 대한 액세스를 제공합니다.

-`ctx.headers`
-`ctx.query`
-`ctx.path_params`
-`ctx.body_bytes()`

예:

```python
@app.post("/events")
async def create_event(ctx: Context):
    ua = ctx.headers.get("user-agent", "unknown")
    size = len(ctx.body_bytes())
    return {"received": size, "ua": ua}
```
