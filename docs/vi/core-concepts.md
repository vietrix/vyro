# Khái niệm cốt lõi

## Mô hình thiết kế

- Python khai báo routes và handlers
- Rust thực thi networking và runtime
- `Context` mang metadata của request

## Quy tắc handler

- Bắt buộc dùng `async def`
- Tham số đầu tiên phải là `ctx`
- Các tham số typed bổ sung được bind từ route/query

## Quyền sở hữu runtime

`app.run()` khởi động native runtime và mô hình workers.
