# OpenAPI と API コントラクト

OpenAPI を生成します。

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

互換性を比較します:

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

API の破壊的な変更を防ぐために、これを CI で使用します。