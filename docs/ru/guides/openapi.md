# OpenAPI and API Contracts

Generate OpenAPI:

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

Compare compatibility:

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

Use this in CI to prevent breaking API changes.
