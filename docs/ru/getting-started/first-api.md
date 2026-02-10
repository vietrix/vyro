# Первый API

В этом примере показаны параметры пути, доступ к запросу и ответ JSON.

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## Типы ответов

- `dict` / `list` -> JSON
- `str` -> текстовый ответ
- `bytes` -> двоичный ответ
- `(body, status)`
- `(body, status, headers)`