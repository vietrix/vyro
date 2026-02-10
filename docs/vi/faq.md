# FAQ

## Vyro có phải để thay thế FastAPI không?

Vyro hướng đến Python DX + Rust execution engine. Bạn nên đánh giá theo workload, latency target và mô hình vận hành của hệ thống.

## Vì sao docs có nhắc `python -m vyro`?

`vyro` là lệnh chính cho end-user. `python -m vyro` chỉ là fallback khi PATH trên máy bạn chưa nhận script `vyro`.

## Người dùng cuối có nên chạy `scripts.dev.*` không?

Không. End-user dùng `vyro ...`. Các script trong `scripts.dev` là tooling nội bộ cho developer.

## Vyro có hỗ trợ WebSocket không?

Có. Vyro hỗ trợ qua runtime edge primitives và route-level WebSocket handlers.

## Có chạy được trên Python 3.13 không?

Có. Vyro target Python 3.10-3.13.
