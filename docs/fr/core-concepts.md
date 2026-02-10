# Concepts de base

## Modèle de conception

- Python déclare les routes et les gestionnaires
- Rust exécute le travail de mise en réseau/d'exécution
- `Context` transporte les métadonnées de la demande

## Règles du gestionnaire

- Doit être `async def`
- Le premier argument doit être `ctx`
- Des arguments tapés supplémentaires sont liés à la route/requête

## Propriété du runtime

`app.run()` démarre le runtime natif et le modèle de travail.