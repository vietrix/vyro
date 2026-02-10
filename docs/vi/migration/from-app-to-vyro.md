# Hướng dẫn migration: `App` sang `Vyro`

## Breaking change

Trước đây:

```python
from vyro import App
app = App()
```

Hiện tại:

```python
from vyro import Vyro
app = Vyro()
```

Không còn alias `App`. Bạn cần cập nhật import trực tiếp sang `Vyro`.
