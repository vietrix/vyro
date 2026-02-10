# 라우팅

## 경로 DSL

- `/users/:id` -> 명명된 매개변수
- `/static/*` -> 포괄

## 버전 관리 및 지원 중단

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## 오류

잘못된 서명이나 모호한 경로로 인해 `RouteDefinitionError` / `HandlerSignatureError`가 발생합니다.