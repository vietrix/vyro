# 첫 번째 API

이 예제는 path 파라미터, query 접근, JSON 응답을 보여줍니다.

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## 응답 타입

- `dict` / `list` -> JSON
- `str` -> 텍스트 응답
- `bytes` -> 바이너리 응답
- `(body, status)`
- `(body, status, headers)`
