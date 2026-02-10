# Guide de migration : application vers Vyro

## Briser le changement

Vieux:

```python
from vyro import App
app = App()
```

Nouveau:

```python
from vyro import Vyro
app = Vyro()
```

Aucun alias `App` n’est fourni. Mettez à jour les importations directement.