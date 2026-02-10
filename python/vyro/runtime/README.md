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
- Native async outbound HTTP client primitives.
- HTTP/2 stream helper primitives.
- gRPC gateway mapping/transcoding foundation primitives.
- Streaming multipart upload collector primitives.
- High-performance multipart parser primitives.
- Static file serving primitives with safe path resolution.
- Outbound circuit-breaker primitives for unstable upstreams.
- Outbound bulkhead isolation primitives per dependency.
- Retry policy primitives with exponential backoff and jitter.
- Timeout budget primitives for cross-call deadline propagation.
- WebSocket route registry primitives for async handlers.

## Entry Points
- `run_native_server`

## Not Here
- Route normalization and context schema.
