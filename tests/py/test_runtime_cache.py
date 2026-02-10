from __future__ import annotations

import time

from vyro.runtime.platform.cache import MemoryCacheBackend, RedisCacheBackend


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key):  # type: ignore[no-untyped-def]
        return self.store.get(key)

    def set(self, key, value):  # type: ignore[no-untyped-def]
        self.store[key] = value

    def setex(self, key, ttl, value):  # type: ignore[no-untyped-def]
        self.store[key] = value

    def delete(self, key):  # type: ignore[no-untyped-def]
        self.store.pop(key, None)


def test_memory_cache_backend_set_get_delete_and_ttl() -> None:
    cache = MemoryCacheBackend()
    cache.set("k1", "v1")
    assert cache.get("k1") == "v1"
    cache.delete("k1")
    assert cache.get("k1") is None

    cache.set("k2", "v2", ttl_sec=0.01)
    time.sleep(0.02)
    assert cache.get("k2") is None


def test_redis_cache_backend_uses_prefix_and_operations() -> None:
    redis = FakeRedis()
    cache = RedisCacheBackend(client=redis, prefix="app:")
    cache.set("k", "v")
    assert redis.store["app:k"] == "v"
    assert cache.get("k") == "v"
    cache.delete("k")
    assert "app:k" not in redis.store
