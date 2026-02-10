from __future__ import annotations

from typing import Any, Callable

from .middleware import Middleware
from .middleware.registry import MiddlewareRegistry
from .routing.registry import RouterRegistry
from .runtime.backpressure import BackpressureController
from .runtime.concurrency import RouteConcurrencyLimiter
from .runtime.rate_limit import TokenBucketRateLimiter
from .runtime.shutdown import GracefulShutdownPolicy
from .runtime.server import run_native_server
from .settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKERS


class Vyro:
    def __init__(self) -> None:
        self._router = RouterRegistry()
        self._middlewares = MiddlewareRegistry()
        self._shutdown_policy = GracefulShutdownPolicy()
        self._backpressure = BackpressureController()
        self._concurrency = RouteConcurrencyLimiter()
        self._rate_limiter = TokenBucketRateLimiter(rate_per_sec=1000.0, burst=2000)

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

    def run(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        workers: int = DEFAULT_WORKERS,
    ) -> None:
        compiled_plan = self._router.compile()
        run_native_server(host, port, max(workers, 1), compiled_plan)
