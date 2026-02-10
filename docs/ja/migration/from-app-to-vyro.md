# Migration Guide: App to Vyro

## Breaking change

Old:

```python
from vyro import App
app = App()
```

New:

```python
from vyro import Vyro
app = Vyro()
```

No `App` alias is provided. Update imports directly.
