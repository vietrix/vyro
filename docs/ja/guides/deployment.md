# Deployment

## Checklist

1. Set `VYRO_ENV=production`
2. Configure strong `VYRO_SECRET_KEY`
3. Set worker count from CPU profile
4. Enable observability and health probes
5. Validate API contract before rollout

## Kubernetes

Generate manifests:

```bash
vyro k8s --name vyro-api --image ghcr.io/vietrix/vyro:latest --out k8s.yaml
```
