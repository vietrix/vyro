from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ServiceEndpoint:
    service: str
    host: str
    port: int
    scheme: str = "http"
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"


class DiscoveryAdapter(Protocol):
    def resolve(self, service: str) -> list[ServiceEndpoint]:
        ...


@dataclass(slots=True)
class StaticDiscoveryAdapter:
    _services: dict[str, list[ServiceEndpoint]] = field(default_factory=dict)

    def register(self, service: str, endpoint: ServiceEndpoint) -> None:
        self._services.setdefault(service, []).append(endpoint)

    def resolve(self, service: str) -> list[ServiceEndpoint]:
        return list(self._services.get(service, []))


@dataclass(slots=True)
class EnvDiscoveryAdapter:
    prefix: str = "VYRO_DISCOVERY_"
    default_scheme: str = "http"

    def resolve(self, service: str) -> list[ServiceEndpoint]:
        key = f"{self.prefix}{service.upper().replace('-', '_')}"
        raw = os.getenv(key, "").strip()
        if not raw:
            return []
        endpoints: list[ServiceEndpoint] = []
        for chunk in raw.split(","):
            piece = chunk.strip()
            if not piece:
                continue
            host, _, port_raw = piece.partition(":")
            try:
                port = int(port_raw)
            except ValueError:
                continue
            endpoints.append(ServiceEndpoint(service=service, host=host, port=port, scheme=self.default_scheme))
        return endpoints


@dataclass(slots=True)
class ServiceDiscoveryRegistry:
    _adapters: list[DiscoveryAdapter] = field(default_factory=list)

    def register_adapter(self, adapter: DiscoveryAdapter) -> None:
        self._adapters.append(adapter)

    def resolve(self, service: str) -> list[ServiceEndpoint]:
        discovered: list[ServiceEndpoint] = []
        for adapter in self._adapters:
            discovered.extend(adapter.resolve(service))
        return discovered
