# Guide de l'utilisateur CLI

## Modèle de commande

Vyro CLI est divisé en deux surfaces :

1. Commandes de l'utilisateur final (`vyro ...`) pour exécuter et exploiter les applications.
2. Scripts de développeur (`python -m scripts.dev...`) pour les vérifications/construction/bench internes.

## Commandes de l'utilisateur final

- `vyro new` - échafauder un nouveau projet.
- `vyro run` - exécutez l'application en mode production.
- `vyro dev` - exécutez l'application avec un comportement de rechargement.
- `vyro doctor` - valide les conseils d'environnement et de préparation.
- `vyro openapi` - génère OpenAPI à partir des routes d'application.
- `vyro compat` - comparez les contrats API.
- `vyro migrate` - exécute les migrations.
- `vyro drift` - détecte la dérive du schéma.
- `vyro k8s` - génère des manifestes Kubernetes.
- `vyro nogil-tune` - recommande le réglage des travailleurs.
- `vyro release ...` - libère les commandes d'automatisation.

## Scripts réservés aux développeurs

Utilisez-les pour la maintenance du projet, et non pour les opérations d'exécution de l'utilisateur final :

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## Codes de sortie

- `0` : réussite
- `1` : échec d'exécution/d'exécution/outillage
- `2` : entrées/arguments utilisateur non valides