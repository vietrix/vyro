# OpenAPI и контракты API

Создайте OpenAPI:

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

Сравните совместимость:

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

Используйте это в CI, чтобы предотвратить нарушение изменений API.