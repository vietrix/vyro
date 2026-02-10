from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, Protocol


class TransactionAdapter(Protocol):
    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        ...


Handler = Callable[..., Awaitable[Any]]


@dataclass(slots=True)
class TransactionScope:
    adapter_key: str = "db"

    def transactional(self, fn: Handler) -> Handler:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            adapter = self._resolve_adapter(args, kwargs)
            if adapter is None:
                return await fn(*args, **kwargs)
            await adapter.execute("BEGIN")
            try:
                result = await fn(*args, **kwargs)
                await adapter.execute("COMMIT")
                return result
            except Exception:
                await adapter.execute("ROLLBACK")
                raise

        return wrapper

    def _resolve_adapter(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> TransactionAdapter | None:
        adapter = kwargs.get(self.adapter_key)
        if adapter is not None:
            return adapter
        if args:
            ctx = args[0]
            return getattr(ctx, self.adapter_key, None)
        return None
