# Cai dat

## Yeu cau

- Python 3.10+
- pip
- Rust toolchain (chi can khi build tu source)

## Cai tu PyPI

```bash
pip install vyro
```

## Kiem tra cai dat

Lenh chinh cho nguoi dung cuoi (khuyen nghi):

```bash
vyro --help
```

Lenh fallback (khi PATH chua nhan `vyro`):

```bash
python -m vyro --help
```

## Vi sao co 2 cach goi?

- `vyro` la CLI chinh thuc cho end-user.
- `python -m vyro` cung chay dung CLI do, dung de fallback/debug PATH.

## Xu ly loi PATH

Neu khong tim thay `vyro`:

1. Dong/mo lai terminal sau khi cai dat.
2. Kiem tra thu muc Scripts cua Python da co trong PATH.
3. Tam thoi dung `python -m vyro`.

## Thiet lap cho dev

```bash
pip install -e .[dev]
pip install -e .[docs]
```
