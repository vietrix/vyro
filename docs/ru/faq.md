# FAQ

## Is Vyro a FastAPI replacement?

Vyro targets Python DX with a Rust execution engine. Evaluate by your workload, latency goals, and operational model.

## Why does documentation mention `python -m vyro`?

`vyro` is the primary command for end users. `python -m vyro` is a fallback when shell PATH is not configured yet.

## Should users run `scripts.dev.*` commands?

No. End users should use `vyro ...`. Developer scripts are internal maintenance tooling.

## Does Vyro support WebSocket?

Yes, through runtime edge primitives and route-level WebSocket handlers.

## Can I run on Python 3.13?

Yes. Vyro targets Python 3.10-3.13.
