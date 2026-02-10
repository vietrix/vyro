# Demarrage rapide

Creez `app.py`:

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/")
async def hello(ctx: Context):
    return {"message": "hello from vyro"}

if __name__ == "__main__":
    app.run(port=8000, workers=1)
```

Execution:

```bash
python app.py
```

Ou via CLI:

```bash
vyro run --app app:app --port 8000
```
