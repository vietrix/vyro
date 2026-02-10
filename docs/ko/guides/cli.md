# CLI 사용 설명서

## 명령 모델

Vyro CLI는 두 가지 표면으로 분할됩니다.

1. 애플리케이션 실행 및 운영을 위한 최종 사용자 명령(`vyro ...`).
2. 내부 점검/빌드/벤치를 위한 개발자 스크립트(`python -m scripts.dev...`).

## 최종 사용자 명령

- `vyro new` - 새 프로젝트를 발판으로 삼습니다.
- `vyro run` - 프로덕션 스타일 모드에서 앱을 실행합니다.
- `vyro dev` - 다시 로드 동작으로 앱을 실행합니다.
- `vyro doctor` - 환경 및 준비 힌트를 검증합니다.
- `vyro openapi` - 앱 경로에서 OpenAPI를 생성합니다.
- `vyro compat` - API 계약을 비교합니다.
- `vyro migrate` - 마이그레이션을 실행합니다.
- `vyro drift` - 스키마 드리프트를 감지합니다.
- `vyro k8s` - Kubernetes 매니페스트를 생성합니다.
- `vyro nogil-tune` - 작업자 튜닝을 권장합니다.
- `vyro release ...` - 자동화 명령을 해제합니다.

## 개발자 전용 스크립트

최종 사용자 런타임 작업이 아닌 프로젝트 유지 관리에 다음을 사용하십시오.

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## 종료 코드

- `0`: 성공
- `1`: 실행/런타임/툴링 실패
- `2`: 잘못된 사용자 입력/인수