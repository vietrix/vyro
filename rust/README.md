# rust

## Purpose
Native execution engine for vyro.

## Owns
- Tokio runtime and Hyper server.
- Route matching with `matchit`.
- Python callback bridging via PyO3.

## Entry Points
- `rust/src/lib.rs`
- `rust/src/bridge/py_entry.rs`

## Not Here
- Python-facing route declaration syntax.
