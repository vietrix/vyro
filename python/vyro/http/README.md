# http

## Purpose
HTTP-facing data models and helpers for Python handlers.

## Owns
- `Context` wrapper.
- Immutable request core views (`headers`, `query`, `path_params`) and mutable extensions store.
- Request/response view models.
- SSE response primitives (`SSEEvent`, `SSEResponse`).
- Header/query helper utilities.

## Entry Points
- `vyro.http.context.Context`

## Not Here
- Route registration and signature enforcement.
