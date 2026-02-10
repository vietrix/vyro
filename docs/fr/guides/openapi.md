# Contrats OpenAPI et API

Générez OpenAPI :

```bash
vyro openapi --app examples.hello_world:app --out openapi.json
```

Comparez la compatibilité :

```bash
vyro compat --base openapi-prev.json --target openapi.json
```

Utilisez-le dans CI pour éviter de rompre les modifications de l'API.