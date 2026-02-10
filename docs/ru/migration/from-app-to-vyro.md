# Руководство по миграции: приложение на Vyro

## Критическое изменение

Старый:

```python
from vyro import App
app = App()
```

Новый:

```python
from vyro import Vyro
app = Vyro()
```

Псевдоним `App` не указан. Обновите импорт напрямую.