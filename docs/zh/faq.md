＃ 常问问题

## Vyro 是 FastAPI 的替代品吗？

Vyro 的目标是使用 Rust 执行引擎的 Python DX。根据您的工作负载、延迟目标和运营模型进行评估。

## 为什么文档提到`python -m vyro`？

`vyro` 是最终用户的主要命令。 `python -m vyro` 是尚未配置 shell PATH 时的后备方案。

## 用户是否应该运行 `scripts.dev.*` 命令？

否。最终用户应使用 `vyro ...`。开发人员脚本是内部维护工具。

## Vyro 支持 WebSocket 吗？

是的，通过运行时边缘原语和路由级 WebSocket 处理程序。

## 我可以在 Python 3.13 上运行吗？

是的。 Vyro 的目标是 Python 3.10-3.13。