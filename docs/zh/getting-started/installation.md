＃ 安装

＃＃ 要求

-Python 3.10+
- 点
- Rust 工具链（仅源代码构建需要）

## 从 PyPI 安装

```bash
pip install vyro
```

## 验证安装

主要（建议最终用户使用）：

```bash
vyro --help
```

后备（如果您的 shell PATH 尚未公开 `vyro`）：

```bash
python -m vyro --help
```

## 为什么有两个命令？

- `vyro` 是官方最终用户 CLI 命令。
- `python -m vyro` 直接运行相同的 CLI 模块，对于 PATH/调试场景很有用。

## 路径故障排除

如果没有找到`vyro`：

1.安装后重新打开终端。
2. 确保 Python 脚本目录位于 PATH 中。
3、暂时使用`python -m vyro`。

## 开发者设置

```bash
pip install -e .[dev]
pip install -e .[docs]
```
