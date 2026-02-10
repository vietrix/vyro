from __future__ import annotations

from vyro.runtime.platform.cache import MemoryCacheBackend
from vyro.runtime.platform.cache_invalidation import CacheInvalidationHooks


def test_cache_invalidation_hooks_trigger_on_set_and_delete() -> None:
    backend = MemoryCacheBackend()
    hooks = CacheInvalidationHooks()
    events: list[str] = []
    hooks.on_set(lambda key: events.append(f"set:{key}"))
    hooks.on_delete(lambda key: events.append(f"del:{key}"))

    hooks.set(backend, "k1", "v1")
    hooks.delete(backend, "k1")

    assert events == ["set:k1", "del:k1"]


def test_cache_invalidation_hooks_apply_write_to_backend() -> None:
    backend = MemoryCacheBackend()
    hooks = CacheInvalidationHooks()
    hooks.set(backend, "k2", "v2", ttl_sec=0.5)
    assert backend.get("k2") == "v2"
