# 故障排除

## ZXQ代码0ZXQ

使用 `<module>:<attribute>`，例如 `examples.hello_world:app`。

## 路由签名错误

确保处理程序是 `async def` 并且第一个参数是 `ctx`。

## 本机构建问题

安装 Rust 工具链并使用 `maturin build --release` 进行重建。

## 文档构建错误

运行 `mkdocs build --strict` 并修复损坏的链接或丢失的页面。