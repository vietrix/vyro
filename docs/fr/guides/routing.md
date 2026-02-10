# Routage

## Chemin DSL

- `/users/:id` -> paramètre nommé
- `/static/*` -> fourre-tout

## Gestion des versions et dépréciation

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## Erreurs

Les signatures invalides ou les itinéraires ambigus génèrent `RouteDefinitionError` / `HandlerSignatureError`.