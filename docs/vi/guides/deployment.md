# Triển khai

## Checklist

1. Set `VYRO_ENV=production`
2. Cấu hình `VYRO_SECRET_KEY` đủ mạnh
3. Chọn số workers theo CPU profile
4. Bật observability và health probes
5. Kiểm tra API contract trước khi rollout

## Kubernetes

Sinh manifest:

```bash
vyro k8s --name vyro-api --image ghcr.io/vietrix/vyro:latest --out k8s.yaml
```
