# Contexte et requête/réponse

`Context` donne accès aux métadonnées de la requête :

- `ctx.headers`
- `ctx.query`
- `ctx.path_params`
- `ctx.body_bytes()`

Exemple:

```python
@app.post("/events")
async def create_event(ctx: Context):
    ua = ctx.headers.get("user-agent", "unknown")
    size = len(ctx.body_bytes())
    return {"received": size, "ua": ua}
```
