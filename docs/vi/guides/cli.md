# Hướng dẫn CLI cho người dùng

## Mô hình lệnh

CLI của Vyro tách làm 2 lớp rõ ràng:

1. Lệnh end-user (`vyro ...`) để chạy và vận hành ứng dụng.
2. Script developer (`python -m scripts.dev...`) để check/build/benchmark nội bộ.

## Lệnh end-user

- `vyro new` - tạo skeleton dự án mới.
- `vyro run` - chạy app theo mode production-style.
- `vyro dev` - chạy app với reload.
- `vyro doctor` - kiểm tra môi trường và gợi ý readiness.
- `vyro openapi` - sinh OpenAPI từ route app.
- `vyro compat` - so sánh API contract.
- `vyro migrate` - chạy migration.
- `vyro drift` - phát hiện schema drift.
- `vyro k8s` - sinh Kubernetes manifest.
- `vyro nogil-tune` - gợi ý tuning workers.
- `vyro release ...` - nhóm lệnh release automation.

## Script chỉ dành cho developer

Dùng cho bảo trì dự án, không phải luồng runtime cho end-user:

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## Exit codes

- `0`: thành công
- `1`: lỗi thực thi/runtime/tooling
- `2`: sai input/argument
