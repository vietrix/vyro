# FAQ

## Vyro co phai de thay the FastAPI khong?

Vyro huong den Python DX + Rust execution engine. Ban nen danh gia theo workload, latency target va mo hinh van hanh cua he thong.

## Vi sao docs co nhac `python -m vyro`?

`vyro` la lenh chinh cho end-user. `python -m vyro` chi la fallback khi PATH tren may ban chua nhan script `vyro`.

## Nguoi dung cuoi co nen chay `scripts.dev.*` khong?

Khong. End-user dung `vyro ...`. Cac script trong `scripts.dev` la tooling noi bo cho developer.

## Vyro co ho tro WebSocket khong?

Co. Vyro co runtime edge primitives va route-level WebSocket handler.

## Co chay duoc tren Python 3.13 khong?

Co. Vyro target Python 3.10-3.13.
