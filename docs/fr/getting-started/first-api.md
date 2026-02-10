# Première API

Cet exemple montre les paramètres de chemin, l'accès aux requêtes et la réponse JSON.

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/users/:id")
async def get_user(ctx: Context, id: int):
    verbose = ctx.query.get("verbose", "false")
    return {"id": id, "verbose": verbose == "true"}
```

## Types de réponses

- `dict` / `list` -> JSON
- `str` -> réponse texte
- `bytes` -> réponse binaire
- `(body, status)`
- `(body, status, headers)`