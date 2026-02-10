#Installation

## Exigences

-Python 3.10+
- pépin
- Chaîne d'outils Rust (requis uniquement pour les versions sources)

## Installer depuis PyPI

```bash
pip install vyro
```

## Vérifier l'installation

Principal (recommandé pour les utilisateurs finaux) :

```bash
vyro --help
```

Solution de secours (si votre shell PATH n'expose pas encore `vyro`) :

```bash
python -m vyro --help
```

## Pourquoi deux commandes ?

- `vyro` est la commande CLI officielle de l'utilisateur final.
- `python -m vyro` exécute directement le même module CLI et est utile pour les scénarios PATH/debug.

## Dépannage du CHEMIN

Si `vyro` est introuvable :

1. Rouvrez le terminal après l'installation.
2. Assurez-vous que le répertoire des scripts Python se trouve sur PATH.
3. Utilisez temporairement `python -m vyro`.

## Configuration du développeur

```bash
pip install -e .[dev]
pip install -e .[docs]
```
