# Huong dan CLI cho nguoi dung

## Mo hinh lenh

CLI cua Vyro tach lam 2 lop ro rang:

1. Lenh end-user (`vyro ...`) de chay va van hanh ung dung.
2. Script developer (`python -m scripts.dev...`) de check/build/benchmark noi bo.

## Lenh end-user

- `vyro new` - tao skeleton du an moi.
- `vyro run` - chay app theo mode production-style.
- `vyro dev` - chay app voi reload.
- `vyro doctor` - kiem tra moi truong va goi y readiness.
- `vyro openapi` - sinh OpenAPI tu route app.
- `vyro compat` - so sanh API contract.
- `vyro migrate` - chay migration.
- `vyro drift` - phat hien schema drift.
- `vyro k8s` - sinh Kubernetes manifest.
- `vyro nogil-tune` - goi y tuning workers.
- `vyro release ...` - nhom lenh release automation.

## Script chi danh cho dev

Dung cho bao tri du an, khong phai luong runtime cho end-user:

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## Exit codes

- `0`: thanh cong
- `1`: loi thuc thi/runtime/tooling
- `2`: sai input/argument
