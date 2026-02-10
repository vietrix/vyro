from __future__ import annotations

from typing import Any, Callable

from .middleware import Middleware
from .middleware.registry import MiddlewareRegistry
from .routing.registry import RouterRegistry
from .runtime.backpressure import BackpressureController
from .runtime.bulkhead import OutboundBulkhead
from .runtime.circuit_breaker import OutboundCircuitBreaker
from .runtime.concurrency import RouteConcurrencyLimiter
from .runtime.http_client import AsyncHttpClient
from .runtime.http2 import Http2StreamManager
from .runtime.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter
from .runtime.retry import RetryPolicy
from .runtime.shutdown import GracefulShutdownPolicy
from .runtime.server import run_native_server
from .runtime.timeout_budget import TimeoutBudget
from .runtime.websocket import WebSocketRouteRegistry
from .settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKERS


class Vyro:
    def __init__(self) -> None:
        self._router = RouterRegistry()
        self._middlewares = MiddlewareRegistry()
        self._shutdown_policy = GracefulShutdownPolicy()
        self._backpressure = BackpressureController()
        self._concurrency = RouteConcurrencyLimiter()
        self._rate_limiter = TokenBucketRateLimiter(rate_per_sec=1000.0, burst=2000)
        self._multi_rate_limiter = MultiKeyRateLimiter(rate_per_sec=500.0, burst=1000)
        self._http_client = AsyncHttpClient()
        self._http2_streams = Http2StreamManager()
        self._outbound_circuit_breaker = OutboundCircuitBreaker()
        self._outbound_bulkhead = OutboundBulkhead()
        self._retry_policy = RetryPolicy()
        self._timeout_budget = TimeoutBudget(timeout_sec=30.0)
        self._websocket = WebSocketRouteRegistry()

    def get(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("GET", path, version=version, deprecated=deprecated)

    def post(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("POST", path, version=version, deprecated=deprecated)

    def put(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("PUT", path, version=version, deprecated=deprecated)

    def delete(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("DELETE", path, version=version, deprecated=deprecated)

    def websocket(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
            self._websocket.add(path, handler)
            return handler

        return decorator

    def add_middleware(
        self,
        mw: Middleware,
        *,
        priority: int | None = None,
        group: str | None = None,
    ) -> None:
        self._middlewares.add(mw, priority=priority, group=group)

    def set_shutdown_policy(self, policy: GracefulShutdownPolicy) -> None:
        self._shutdown_policy = policy

    def set_backpressure(self, controller: BackpressureController) -> None:
        self._backpressure = controller

    def set_concurrency_limiter(self, limiter: RouteConcurrencyLimiter) -> None:
        self._concurrency = limiter

    def set_rate_limiter(self, limiter: TokenBucketRateLimiter) -> None:
        self._rate_limiter = limiter

    def set_multi_rate_limiter(self, limiter: MultiKeyRateLimiter) -> None:
        self._multi_rate_limiter = limiter

    def set_http_client(self, client: AsyncHttpClient) -> None:
        self._http_client = client

    def set_http2_stream_manager(self, manager: Http2StreamManager) -> None:
        self._http2_streams = manager

    def set_outbound_circuit_breaker(self, breaker: OutboundCircuitBreaker) -> None:
        self._outbound_circuit_breaker = breaker

    def set_outbound_bulkhead(self, bulkhead: OutboundBulkhead) -> None:
        self._outbound_bulkhead = bulkhead

    def set_retry_policy(self, policy: RetryPolicy) -> None:
        self._retry_policy = policy

    def set_timeout_budget(self, budget: TimeoutBudget) -> None:
        self._timeout_budget = budget

    def run(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        workers: int = DEFAULT_WORKERS,
    ) -> None:
        compiled_plan = self._router.compile()
        run_native_server(host, port, max(workers, 1), compiled_plan)
