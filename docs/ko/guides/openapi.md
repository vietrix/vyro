# OpenAPI 및 API 계약

OpenAPI 생성:

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

호환성 비교:

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

API 변경이 중단되는 것을 방지하려면 CI에서 이를 사용하십시오.