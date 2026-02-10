# http

## Purpose
HTTP transport layer for request intake and response output.

## Owns
- Hyper server loop.
- Request/response data models.
- Zero-copy request body handoff via `bytes::Bytes`.
- Query and header parsing.

## Entry Points
- `http::server::serve`

## Not Here
- Python route parsing and release scripts.
