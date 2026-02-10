＃ ルーティング

## パス DSL

- `/users/:id` -> 名前付きパラメータ
- `/static/*` -> キャッチオール

## バージョン管理と非推奨化

```python
@app.get("/v1/items/:id", version="v1", deprecated="use /v2")
async def get_item(ctx: Context, id: int):
    return {"id": id}
```

## エラー

無効な署名または曖昧なルートでは、`RouteDefinitionError` / `HandlerSignatureError` が発生します。