# 배포

## 체크리스트

1. `VYRO_ENV=production` 설정
2. 강력한 `VYRO_SECRET_KEY` 구성
3. CPU 프로필에서 작업자 수 설정
4. 관찰 가능성 및 상태 프로브 활성화
5. 출시 전 API 계약 검증

## 쿠버네티스

매니페스트를 생성합니다.

```bash
vyro k8s --name vyro-api --image ghcr.io/vietrix/vyro:latest --out k8s.yaml
```
