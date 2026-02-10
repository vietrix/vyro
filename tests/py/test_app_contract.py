import pytest

from vyro import Vyro
from vyro.errors import HandlerSignatureError
from vyro.runtime.backpressure import BackpressureController
from vyro.runtime.bulkhead import OutboundBulkhead
from vyro.runtime.circuit_breaker import OutboundCircuitBreaker
from vyro.runtime.concurrency import RouteConcurrencyLimiter
from vyro.runtime.grpc_gateway import GrpcGateway
from vyro.runtime.http_client import AsyncHttpClient
from vyro.runtime.http2 import Http2StreamManager
from vyro.runtime.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter
from vyro.runtime.retry import RetryPolicy
from vyro.runtime.shutdown import GracefulShutdownPolicy
from vyro.runtime.timeout_budget import TimeoutBudget


def test_sync_handler_is_rejected() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError):

        @app.get("/users/:id")
        def sync_handler(ctx):  # type: ignore[no-untyped-def]
            return {"ok": True}


def test_app_symbol_is_removed() -> None:
    with pytest.raises(ImportError):
        from vyro import App  # type: ignore[attr-defined]  # noqa: F401


def test_first_param_must_be_ctx() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="first argument must be named 'ctx'"):

        @app.get("/users/:id")
        async def invalid(first, id: int):  # type: ignore[no-untyped-def]
            return {"id": id}


def test_handler_must_have_ctx_param() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="must accept first argument 'ctx'"):

        @app.get("/users/:id")
        async def invalid():  # type: ignore[no-untyped-def]
            return {"ok": True}


def test_sync_websocket_handler_is_rejected() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="websocket handler must be declared with async def"):

        @app.websocket("/ws/:room")
        def sync_ws(ctx):  # type: ignore[no-untyped-def]
            return ctx


def test_websocket_handler_is_registered() -> None:
    app = Vyro()

    @app.websocket("/ws/:room")
    async def ws_handler(ctx):  # type: ignore[no-untyped-def]
        return ctx

    assert app._websocket.get("/ws/:room") is ws_handler  # noqa: SLF001


def test_vyro_accepts_custom_shutdown_policy() -> None:
    app = Vyro()
    policy = GracefulShutdownPolicy(timeout_seconds=12, drain_inflight=False)
    app.set_shutdown_policy(policy)
    assert app._shutdown_policy.timeout_seconds == 12  # noqa: SLF001
    assert app._shutdown_policy.drain_inflight is False  # noqa: SLF001


def test_vyro_accepts_custom_backpressure_controller() -> None:
    app = Vyro()
    controller = BackpressureController(max_inflight=8)
    app.set_backpressure(controller)
    assert app._backpressure.max_inflight == 8  # noqa: SLF001


def test_vyro_accepts_custom_concurrency_limiter() -> None:
    app = Vyro()
    limiter = RouteConcurrencyLimiter(default_limit=12)
    app.set_concurrency_limiter(limiter)
    assert app._concurrency.default_limit == 12  # noqa: SLF001


def test_vyro_accepts_custom_rate_limiter() -> None:
    app = Vyro()
    limiter = TokenBucketRateLimiter(rate_per_sec=5.0, burst=10)
    app.set_rate_limiter(limiter)
    assert app._rate_limiter.burst == 10  # noqa: SLF001


def test_vyro_accepts_custom_multi_key_rate_limiter() -> None:
    app = Vyro()
    limiter = MultiKeyRateLimiter(rate_per_sec=12.0, burst=24)
    app.set_multi_rate_limiter(limiter)
    assert app._multi_rate_limiter.burst == 24  # noqa: SLF001


def test_vyro_accepts_custom_http_client() -> None:
    app = Vyro()
    client = AsyncHttpClient()
    app.set_http_client(client)
    assert app._http_client is client  # noqa: SLF001


def test_vyro_accepts_custom_http2_stream_manager() -> None:
    app = Vyro()
    manager = Http2StreamManager()
    app.set_http2_stream_manager(manager)
    assert app._http2_streams is manager  # noqa: SLF001


def test_vyro_accepts_custom_grpc_gateway() -> None:
    app = Vyro()
    gateway = GrpcGateway()
    app.set_grpc_gateway(gateway)
    assert app._grpc_gateway is gateway  # noqa: SLF001


def test_vyro_accepts_custom_outbound_circuit_breaker() -> None:
    app = Vyro()
    breaker = OutboundCircuitBreaker(failure_threshold=2, recovery_timeout_sec=1.5)
    app.set_outbound_circuit_breaker(breaker)
    assert app._outbound_circuit_breaker.failure_threshold == 2  # noqa: SLF001


def test_vyro_accepts_custom_outbound_bulkhead() -> None:
    app = Vyro()
    bulkhead = OutboundBulkhead(default_limit=4)
    app.set_outbound_bulkhead(bulkhead)
    assert app._outbound_bulkhead.default_limit == 4  # noqa: SLF001


def test_vyro_accepts_custom_retry_policy() -> None:
    app = Vyro()
    policy = RetryPolicy(max_attempts=5, base_delay_sec=0.2)
    app.set_retry_policy(policy)
    assert app._retry_policy.max_attempts == 5  # noqa: SLF001


def test_vyro_accepts_custom_timeout_budget() -> None:
    app = Vyro()
    budget = TimeoutBudget(timeout_sec=2.5)
    app.set_timeout_budget(budget)
    assert app._timeout_budget.timeout_sec == pytest.approx(2.5)  # noqa: SLF001
