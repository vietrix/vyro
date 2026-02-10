# 첫 번째 API

이 예에서는 경로 매개변수, 쿼리 액세스 및 JSON 응답을 보여줍니다.

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## 응답 유형

- `dict` / `list` -> JSON
- `str` -> 텍스트 응답
- `bytes` -> 바이너리 응답
-`(body, status)`
-`(body, status, headers)`