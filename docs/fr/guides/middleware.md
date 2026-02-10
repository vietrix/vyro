# Intergiciel

Enregistrez le middleware avec une commande explicite :

```python
app.add_middleware(my_middleware, priority=100)
```

## Recommandations

- Gardez le middleware pur et rapide
- Utiliser des priorités explicites
- Conserver les travaux gourmands en E/S dans les primitives d'exécution

## Idempotence

Utilisez un middleware d'idempotence pour les points de terminaison d'écriture afin d'éviter les effets secondaires en double.