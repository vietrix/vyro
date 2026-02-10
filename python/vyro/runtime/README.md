# runtime

## Purpose
Runtime-facing primitives grouped by domain for clearer ownership.

## Owns
- `resilience`: limits, retries, timeout budgets, backpressure.
- `security`: authn/authz, secrets, tenant/cors/csrf.
- `data`: sql/migrations/transaction/cqrs/outbox.
- `async_ops`: jobs/cron/saga/event bus/task tracing.
- `edge`: client/http2/ws/grpc/multipart/static/compression/etag.
- `platform`: rollout/discovery/k8s/nogil/cache/plugins/flags.

## Entry Points
- `vyro.runtime` (stable symbol re-export)
- `vyro.runtime.<domain>` for internal module ownership.

## Not Here
- Application composition (`vyro.app`).
