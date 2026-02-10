# 移行ガイド: アプリから Vyro へ

## 重大な変更

古い：

```python
from vyro import App
app = App()
```

新しい：

```python
from vyro import Vyro
app = Vyro()
```

`App` エイリアスは提供されません。インポートを直接更新します。