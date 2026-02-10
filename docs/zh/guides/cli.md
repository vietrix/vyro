# CLI 用户指南

## 命令模型

Vyro CLI 分为两个表面：

1. 用于运行和操作应用程序的最终用户命令 (`vyro ...`)。
2. 用于内部检查/构建/基准测试的开发人员脚本 (`python -m scripts.dev...`)。

## 最终用户命令

- `vyro new` - 搭建一个新项目。
- `vyro run` - 在生产风格模式下运行应用程序。
- `vyro dev` - 运行具有重新加载行为的应用程序。
- `vyro doctor` - 验证环境和准备情况提示。
- `vyro openapi` - 从应用程序路由生成 OpenAPI。
- `vyro compat` - 比较 API 合约。
- `vyro migrate` - 执行迁移。
- `vyro drift` - 检测模式漂移。
- `vyro k8s` - 生成 Kubernetes 清单。
- `vyro nogil-tune` - 建议工人调整。
- `vyro release ...` - 发布自动化命令。

## 仅供开发人员使用的脚本

将它们用于项目维护，而不是最终用户运行时操作：

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## 退出代码

- `0`：成功
- `1`：执行/运行时/工具失败
- `2`：无效的用户输入/参数