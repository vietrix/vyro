# vyro

[![CI](https://github.com/vietrix/vyro/actions/workflows/ci.yml/badge.svg)](https://github.com/vietrix/vyro/actions/workflows/ci.yml)
[![Release](https://github.com/vietrix/vyro/actions/workflows/release.yml/badge.svg)](https://github.com/vietrix/vyro/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/vyro.svg)](https://pypi.org/project/vyro/)
[![Python Versions](https://img.shields.io/pypi/pyversions/vyro.svg)](https://pypi.org/project/vyro/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Vyro is a backend framework that combines Python developer experience with a Rust-native execution engine.

## Why Vyro

- Rust-native runtime for high throughput and low overhead.
- Pythonic routing and handler authoring.
- Async-first handler model (`async def` only).
- RBAC/ABAC authorization core primitives.
- API key manager and rotation hook primitives.
- Structured release automation (tag -> changelog -> PyPI -> GitHub Release).
- Native file-path response streaming (return `pathlib.Path` from handler).
- OpenAPI 3.1 + JSON schema generation from route handlers.
- Priority-aware middleware ordering primitives.
- Route-group conditional middleware registration.
- Automatic correlation-id injection on request context.
- Structured JSON logging primitives for CLI/runtime output.
- Configurable log sampling policy (`VYRO_LOG_SAMPLE_INFO/WARN/ERROR`).
- Sensitive field redaction in logs (`VYRO_LOG_REDACT_KEYS`).
- OpenTelemetry-friendly trace span exporter with `traceparent` propagation.
- Prometheus metrics registry primitives (`vyro_requests_total` baseline).
- Built-in latency tracker with p50/p95/p99 quantiles.
- Per-route throughput counters for method/path traffic visibility.
- Health probe primitives for liveness/readiness/startup checks.
- Graceful shutdown policy primitives with timeout/drain controls.
- Runtime backpressure controller for inflight request limits.
- Per-route concurrency limiter for hotspot endpoint control.
- Global token-bucket rate limiter with burst support.
- Multi-key rate limiter for compound identities (IP/user/token).
- Native async outbound HTTP client primitive.
- ETag generation and conditional-request primitives.
- JWT auth guard primitives (issue/verify/authorize).
- HTTP/2 stream helper primitives.
- gRPC gateway mapping/transcoding foundation primitives.
- Streaming multipart upload collector primitives.
- High-performance multipart parser primitives.
- Content negotiation primitives for `Accept` header matching.
- OAuth2/OIDC helper primitives.
- Static file serving primitives with safe path resolution.
- Response compression primitives with speed/balanced/size profiles.
- CORS policy profile primitives (`strict`, `standard`, `permissive`).
- CSRF token issue/verify primitives.
- Outbound circuit-breaker primitive for upstream dependency protection.
- Outbound bulkhead primitive to isolate dependency pools.
- Retry policy primitive with exponential backoff and jitter.
- Timeout budget primitive for end-to-end deadline propagation.
- First-class SSE response primitive for server-sent events.
- WebSocket route registry and `@app.websocket(...)` decorator.

## Quickstart

### Install from PyPI

```bash
pip install vyro
```

### Local development setup

```bash
pip install maturin pytest
maturin build --release
pip install --force-reinstall target/wheels/vyro-*.whl
python examples/hello_world.py
```

## Minimal example

```python
from vyro import Context, Vyro

app = Vyro()

@app.get("/")
async def hello(ctx: Context):
    return {"message": "hello from vyro"}

@app.get("/users/:id", version="1")
async def get_user(ctx: Context, id: int):
    return {"id": id}

@app.get("/legacy", deprecated="use /v2/users/:id")
async def legacy(ctx: Context):
    return {"legacy": True}

if __name__ == "__main__":
    app.run(port=8000, workers=2)
```

## Development

Run all core checks locally:

```bash
cargo test
python -m pytest tests/py tests/integration -q
maturin build --release
```

## CLI

Vyro ships with an official CLI:

```bash
vyro --help
vyro doctor
vyro run --app examples.hello_world:app --port 8000
vyro openapi --app examples.hello_world:app --out openapi.json
vyro compat --base openapi-prev.json --target openapi.json
vyro release notes --tag v0.1.0 --out release_notes.md
```

You can also run it as a module:

```bash
python -m vyro --help
```

`vyro check` includes static route signature linting (`async def` + first arg `ctx`).

## Migration (`App` -> `Vyro`)

```python
# before
from vyro import App
app = App()

# after
from vyro import Vyro
app = Vyro()
```

## Project structure

- `python/vyro/`: user-facing Python APIs.
- `rust/src/`: native runtime and bridge.
- `tests/`: Python, Rust, and integration tests.
- `.github/workflows/`: CI and release automation.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full module map and request flow.

## Community

- Contributing guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Code of Conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- Security policy: [`SECURITY.md`](SECURITY.md)

## License

Vyro is licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).
