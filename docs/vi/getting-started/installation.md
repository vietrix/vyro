# Cài đặt

## Yêu cầu

- Python 3.10 trở lên
- pip
- Rust toolchain (chỉ cần khi build từ source)

## Cài từ PyPI

```bash
pip install "vyro>=0.2.2" --only-binary=:all:
```

## Kiểm tra cài đặt

Lệnh chính cho người dùng cuối (khuyến nghị):

```bash
vyro --help
```

Lệnh dự phòng khi shell chưa nhận `vyro` trong PATH:

```bash
python -m vyro --help
```

## Vì sao có 2 cách gọi?

- `vyro` là CLI chính thức cho người dùng cuối.
- `python -m vyro` chạy cùng một CLI module, dùng để fallback hoặc debug PATH.

## Xử lý lỗi PATH

Nếu hệ thống báo không tìm thấy `vyro`:

1. Đóng và mở lại terminal sau khi cài.
2. Kiểm tra thư mục Scripts của Python đã nằm trong PATH.
3. Dùng tạm `python -m vyro` cho đến khi PATH đúng.

## Thiết lập cho developer

```bash
pip install -e .[dev]
pip install -e .[docs]
```
