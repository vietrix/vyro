# runtime

## Purpose
Bootstrap helpers for invoking native runtime from Python.

## Owns
- Default host/port/worker wiring.
- Native `start_server` call boundary.
- Graceful shutdown policy primitives.
- Backpressure controller primitives.
- Per-route concurrency limiter primitives.
- Global token-bucket rate limiting primitives.
- Multi-key rate-limiting primitives (ip/user/token tuple support).

## Entry Points
- `run_native_server`

## Not Here
- Route normalization and context schema.
