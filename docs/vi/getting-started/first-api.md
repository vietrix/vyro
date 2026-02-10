# API đầu tiên

Ví dụ này minh họa cách nhận path params, đọc query và trả JSON response.

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## Kiểu dữ liệu trả về

- `dict` / `list` -> JSON
- `str` -> text response
- `bytes` -> binary response
- `(body, status)`
- `(body, status, headers)`
