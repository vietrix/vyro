# 第一个 API

此示例显示路径参数、查询访问和 JSON 响应。

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## 响应类型

- `dict` / `list` -> JSON
- `str` -> 文本响应
- `bytes` -> 二进制响应
- `(body, status)`
- ZXQ代码5ZXQ