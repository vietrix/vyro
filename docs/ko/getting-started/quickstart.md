# 빠른 시작

`app.py` 생성:

```python
from vyro import Vyro, Context

app = Vyro()

@app.get("/")
async def hello(ctx: Context):
    return {"message": "hello from vyro"}

if __name__ == "__main__":
    app.run(port=8000, workers=1)
```

달리다:

```bash
python app.py
```

또는 CLI를 통해 실행하세요.

```bash
vyro run --app app:app --port 8000
```
