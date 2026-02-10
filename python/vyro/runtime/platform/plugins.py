from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Protocol


ABI_VERSION = "1.0"


class PluginError(RuntimeError):
    pass


class PluginIncompatibleError(PluginError):
    pass


class PluginProtocol(Protocol):
    name: str
    abi_version: str

    def setup(self, app: Any) -> None:
        ...


@dataclass(frozen=True, slots=True)
class RegisteredPlugin:
    name: str
    abi_version: str
    module: str


@dataclass(slots=True)
class ABIStablePluginSystem:
    abi_version: str = ABI_VERSION
    _plugins: dict[str, RegisteredPlugin] = field(default_factory=dict)

    def register(self, plugin: PluginProtocol, *, module: str = "<dynamic>") -> RegisteredPlugin:
        if plugin.abi_version != self.abi_version:
            raise PluginIncompatibleError(
                f"plugin '{plugin.name}' expects ABI {plugin.abi_version}, runtime ABI is {self.abi_version}"
            )
        record = RegisteredPlugin(name=plugin.name, abi_version=plugin.abi_version, module=module)
        self._plugins[plugin.name] = record
        return record

    def load_from_module(self, module_path: str, app: Any) -> RegisteredPlugin:
        module = import_module(module_path)
        plugin = getattr(module, "plugin", None)
        if plugin is None:
            raise PluginError(f"module '{module_path}' does not expose 'plugin'")
        if not hasattr(plugin, "setup"):
            raise PluginError(f"plugin '{getattr(plugin, 'name', module_path)}' is missing setup(app)")
        record = self.register(plugin, module=module_path)
        plugin.setup(app)
        return record

    def get(self, name: str) -> RegisteredPlugin | None:
        return self._plugins.get(name)

    def all(self) -> tuple[RegisteredPlugin, ...]:
        return tuple(self._plugins.values())
