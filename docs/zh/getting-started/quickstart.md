# 快速入门

创建`app.py`：

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/")
async def hello(ctx: Context):
    return {"message": "hello from vyro"}

if __name__ == "__main__":
    app.run(port=8000, workers=1)
```

跑步：

```bash
python app.py
```

或者通过 CLI 运行：

```bash
vyro run --app app:app --port 8000
```
