# 最初の API

この例では、パス パラメーター、クエリ アクセス、および JSON 応答を示します。

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## 応答タイプ

- `dict` / `list` -> JSON
- `str` -> テキスト応答
- `bytes` -> バイナリ応答
- ZXQコード4ZXQ
- `(body, status, headers)`