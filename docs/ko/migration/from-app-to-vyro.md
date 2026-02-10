# 마이그레이션 가이드: Vyro로의 앱

## 획기적인 변화

오래된:

```python
from vyro import App
app = App()
```

새로운:

```python
from vyro import Vyro
app = Vyro()
```

`App` 별칭은 제공되지 않습니다. 가져오기를 직접 업데이트합니다.