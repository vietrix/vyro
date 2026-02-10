# 部署

## 清单

1.设置`VYRO_ENV=production`
2.配置强`VYRO_SECRET_KEY`
3. 从 CPU 配置文件中设置工作线程数
4. 启用可观察性和运行状况探测
5. 推出前验证 API 合约

## 库伯内特斯

生成清单：

```bash
vyro k8s --name vyro-api --image ghcr.io/vietrix/vyro:latest --out k8s.yaml
```
