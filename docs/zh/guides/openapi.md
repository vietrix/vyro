# OpenAPI 和 API 合约

生成 OpenAPI：

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

比较兼容性：

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

在 CI 中使用它可以防止破坏 API 更改。