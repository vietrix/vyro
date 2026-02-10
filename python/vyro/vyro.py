from __future__ import annotations

from typing import Any, Callable

from .middleware import Middleware
from .middleware.registry import MiddlewareRegistry
from .routing.registry import RouterRegistry
from .runtime.server import run_native_server
from .settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKERS


class Vyro:
    def __init__(self) -> None:
        self._router = RouterRegistry()
        self._middlewares = MiddlewareRegistry()

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("GET", path)

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("POST", path)

    def put(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("PUT", path)

    def delete(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._router.add_route("DELETE", path)

    def add_middleware(self, mw: Middleware) -> None:
        self._middlewares.add(mw)

    def run(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        workers: int = DEFAULT_WORKERS,
    ) -> None:
        compiled_plan = self._router.compile()
        run_native_server(host, port, max(workers, 1), compiled_plan)
