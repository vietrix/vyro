# クイックスタート

`app.py` を作成します。

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/")
async def hello(ctx: Context):
    return {"message": "hello from vyro"}

if __name__ == "__main__":
    app.run(port=8000, workers=1)
```

走る：

```bash
python app.py
```

または、CLI を介して実行します。

```bash
vyro run --app app:app --port 8000
```
