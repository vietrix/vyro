# Installation

## Prérequis

- Python 3.10+
- pip
- Toolchain Rust (requis uniquement pour une compilation depuis les sources)

## Installer depuis PyPI

```bash
pip install vyro
```

## Vérifier l'installation

Commande principale (recommandée pour les utilisateurs finaux) :

```bash
vyro --help
```

Solution de secours (si votre variable PATH n'expose pas encore `vyro`) :

```bash
python -m vyro --help
```

## Pourquoi deux commandes ?

- `vyro` est la commande CLI officielle pour l'utilisateur final.
- `python -m vyro` exécute directement le même module CLI ; utile pour diagnostiquer un problème de PATH.

## Dépannage PATH

Si `vyro` est introuvable :

1. Rouvrez votre terminal après l'installation.
2. Vérifiez que le dossier `Scripts` de Python est présent dans votre PATH.
3. Utilisez temporairement `python -m vyro`.

## Environnement développeur

```bash
pip install -e .[dev]
pip install -e .[docs]
```
