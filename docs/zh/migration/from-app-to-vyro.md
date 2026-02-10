# 迁移指南：应用程序到 Vyro

## 重大改变

老的：

```python
from vyro import App
app = App()
```

新的：

```python
from vyro import Vyro
app = Vyro()
```

未提供 `App` 别名。直接更新导入。