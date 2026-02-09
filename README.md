# vyro

`vyro` is a Rust-powered Python backend framework:
- Rust core for HTTP server, routing, and response building.
- Python API for decorators and business logic.
- Async handler model (`async def`) from day one.

## Quick start

```bash
pip install maturin
maturin develop
python examples/hello_world.py
```

## Current status

- Sprint 1: complete (Rust server can be started from Python).
- Sprint 2: complete (Python-defined routes executed by Rust with `matchit`).
- Sprint 3+ are scaffolded with forward-compatible modules and stubs.
