import pytest

from vyro import Vyro
from vyro.errors import HandlerSignatureError
from vyro.runtime.backpressure import BackpressureController
from vyro.runtime.circuit_breaker import OutboundCircuitBreaker
from vyro.runtime.concurrency import RouteConcurrencyLimiter
from vyro.runtime.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter
from vyro.runtime.retry import RetryPolicy
from vyro.runtime.shutdown import GracefulShutdownPolicy


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


def test_vyro_accepts_custom_outbound_circuit_breaker() -> None:
    app = Vyro()
    breaker = OutboundCircuitBreaker(failure_threshold=2, recovery_timeout_sec=1.5)
    app.set_outbound_circuit_breaker(breaker)
    assert app._outbound_circuit_breaker.failure_threshold == 2  # noqa: SLF001


def test_vyro_accepts_custom_retry_policy() -> None:
    app = Vyro()
    policy = RetryPolicy(max_attempts=5, base_delay_sec=0.2)
    app.set_retry_policy(policy)
    assert app._retry_policy.max_attempts == 5  # noqa: SLF001
