# OpenAPI và API Contracts

Sinh OpenAPI:

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

So sánh compatibility:

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

Dùng bước này trong CI để ngăn breaking API changes.
