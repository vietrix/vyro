# runtime

## Purpose
Bootstrap helpers for invoking native runtime from Python.

## Owns
- Default host/port/worker wiring.
- Native `start_server` call boundary.
- Graceful shutdown policy primitives.
- Backpressure controller primitives.
- Per-route concurrency limiter primitives.

## Entry Points
- `run_native_server`

## Not Here
- Route normalization and context schema.
