# Middleware

Đăng ký middleware với thứ tự rõ ràng:

```python
app.add_middleware(my_middleware, priority=100)
```

## Khuyến nghị

- Giữ middleware thuần và nhanh
- Dùng priority tường minh
- Đẩy phần IO nặng xuống runtime primitives

## Idempotency

Dùng idempotency middleware cho write endpoints để tránh tác dụng phụ lặp.
