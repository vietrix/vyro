# Khắc phục sự cố

## `Invalid --app format`

Dùng định dạng `<module>:<attribute>`, ví dụ `examples.hello_world:app`.

## Lỗi route signature

Đảm bảo handler dùng `async def` và tham số đầu tiên là `ctx`.

## Lỗi build native

Cài Rust toolchain rồi build lại bằng `maturin build --release`.

## Lỗi build docs

Chạy `mkdocs build --strict` và sửa broken links hoặc trang bị thiếu.
