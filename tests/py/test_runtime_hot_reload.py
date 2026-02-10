from __future__ import annotations

import pytest

from vyro.runtime.platform.hot_reload import RuntimeConfigReloadError, SafeRuntimeConfigReloader


def test_hot_reload_loads_initial_snapshot() -> None:
    reloader = SafeRuntimeConfigReloader()
    snapshot = reloader.load_initial({"workers": 2, "log_level": "info", "rate_limit": 100})
    assert snapshot.version == 1
    assert snapshot.get("workers") == 2


def test_hot_reload_applies_patch_and_increments_version() -> None:
    reloader = SafeRuntimeConfigReloader()
    reloader.load_initial({"workers": 1, "log_level": "info", "rate_limit": 100})
    snapshot = reloader.apply({"workers": 4})
    assert snapshot.version == 2
    assert snapshot.get("workers") == 4
    assert snapshot.get("log_level") == "info"


def test_hot_reload_rejects_unsafe_keys() -> None:
    reloader = SafeRuntimeConfigReloader()
    reloader.load_initial({"workers": 1, "log_level": "info", "rate_limit": 100})
    with pytest.raises(RuntimeConfigReloadError, match="not hot-reloadable"):
        reloader.apply({"host": "0.0.0.0"})


def test_hot_reload_rollback_restores_previous_snapshot() -> None:
    reloader = SafeRuntimeConfigReloader()
    reloader.load_initial({"workers": 1, "log_level": "info", "rate_limit": 100})
    reloader.apply({"workers": 8})
    restored = reloader.rollback()
    assert restored.get("workers") == 1
    assert restored.version == 1
