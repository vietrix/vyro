# First API

This example shows path params, query access, and JSON response.

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## Response types

- `dict` / `list` -> JSON
- `str` -> text response
- `bytes` -> binary response
- `(body, status)`
- `(body, status, headers)`
