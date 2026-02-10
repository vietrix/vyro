from __future__ import annotations

import types

import pytest

from vyro import Vyro
from vyro.runtime.plugins import ABIStablePluginSystem, PluginError, PluginIncompatibleError


class _GoodPlugin:
    name = "good"
    abi_version = "1.0"

    def __init__(self) -> None:
        self.installed = False

    def setup(self, app):  # type: ignore[no-untyped-def]
        self.installed = True
        app._plugin_marker = "ok"  # noqa: SLF001


class _BadAbiPlugin:
    name = "bad"
    abi_version = "2.0"

    def setup(self, app):  # type: ignore[no-untyped-def]
        del app


def test_plugin_system_registers_compatible_plugin() -> None:
    system = ABIStablePluginSystem()
    plugin = _GoodPlugin()
    record = system.register(plugin, module="plugins.good")
    assert record.name == "good"
    assert system.get("good") is not None


def test_plugin_system_rejects_incompatible_abi() -> None:
    system = ABIStablePluginSystem()
    with pytest.raises(PluginIncompatibleError, match="expects ABI"):
        system.register(_BadAbiPlugin(), module="plugins.bad")


def test_plugin_system_loads_module_and_runs_setup(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    app = Vyro()
    system = ABIStablePluginSystem()
    plugin = _GoodPlugin()

    fake_module = types.SimpleNamespace(plugin=plugin)

    def fake_import(path):  # type: ignore[no-untyped-def]
        assert path == "my.plugin"
        return fake_module

    monkeypatch.setattr("vyro.runtime.plugins.import_module", fake_import)
    record = system.load_from_module("my.plugin", app)

    assert record.name == "good"
    assert plugin.installed is True
    assert getattr(app, "_plugin_marker", None) == "ok"


def test_plugin_system_requires_exported_plugin_symbol(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    system = ABIStablePluginSystem()

    def fake_import(path):  # type: ignore[no-untyped-def]
        assert path == "empty.plugin"
        return types.SimpleNamespace()

    monkeypatch.setattr("vyro.runtime.plugins.import_module", fake_import)
    with pytest.raises(PluginError, match="does not expose 'plugin'"):
        system.load_from_module("empty.plugin", Vyro())
