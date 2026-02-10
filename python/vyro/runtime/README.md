# runtime

## Purpose
Bootstrap helpers for invoking native runtime from Python.

## Owns
- Default host/port/worker wiring.
- Native `start_server` call boundary.
- RBAC/ABAC authorization core primitives.
- API key manager and rotation hook primitives.
- Security audit log event primitives.
- Memory/Redis cache backend primitives.
- Cache invalidation hook primitives.
- Response cache TTL policy primitives.
- Canary routing control primitives.
- Blue-green rollout helper primitives.
- Safe runtime config hot-reload primitives.
- Graceful shutdown policy primitives.
- Backpressure controller primitives.
- Per-route concurrency limiter primitives.
- Global token-bucket rate limiting primitives.
- Multi-key rate-limiting primitives (ip/user/token tuple support).
- Native async outbound HTTP client primitives.
- ETag generation and conditional-request primitives.
- JWT auth guard primitives (issue/verify/authorize).
- Background jobs runtime primitives.
- Cron scheduler primitives.
- HTTP/2 stream helper primitives.
- gRPC gateway mapping/transcoding foundation primitives.
- Streaming multipart upload collector primitives.
- High-performance multipart parser primitives.
- Migration runner primitives.
- Content negotiation primitives for `Accept`/media-type matching.
- OAuth2/OIDC helper primitives.
- Static file serving primitives with safe path resolution.
- Response compression primitives with configurable profiles.
- CORS policy profile primitives (`strict`, `standard`, `permissive`).
- CSRF token issue/verify primitives.
- DB connection pool manager primitives.
- Dead-letter queue and retry primitives.
- Task trace correlation primitives for background jobs.
- Typed internal event bus primitives.
- CQRS scaffolding primitives (command/query bus).
- Transactional outbox pattern helper primitives.
- Saga orchestration primitives.
- Multi-tenant isolation model primitives.
- Tenant-aware routing and config primitives.
- Feature flag engine primitives for progressive rollout.
- ABI-stable plugin system primitives.
- Extension marketplace manifest primitives.
- Service discovery adapter primitives for multi-service runtime.
- Kubernetes manifest generator primitives.
- No-GIL worker tuning primitives.
- Secrets provider abstraction primitives.
- Async SQL adapter primitives.
- Query timeout and slow query log primitives.
- Schema drift detector primitives.
- Transaction scope decorator primitives.
- Outbound circuit-breaker primitives for unstable upstreams.
- Outbound bulkhead isolation primitives per dependency.
- Retry policy primitives with exponential backoff and jitter.
- Timeout budget primitives for cross-call deadline propagation.
- WebSocket route registry primitives for async handlers.

## Entry Points
- `run_native_server`

## Not Here
- Route normalization and context schema.
