from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol


class SecretsProvider(Protocol):
    def get(self, key: str) -> str | None:
        ...


@dataclass(slots=True)
class EnvSecretsProvider:
    prefix: str = "VYRO_SECRET_"

    def get(self, key: str) -> str | None:
        return os.getenv(f"{self.prefix}{key.upper()}")


@dataclass(slots=True)
class InMemorySecretsProvider:
    values: dict[str, str] = field(default_factory=dict)

    def get(self, key: str) -> str | None:
        return self.values.get(key)


@dataclass(slots=True)
class SecretsManager:
    providers: list[SecretsProvider] = field(default_factory=list)

    def add_provider(self, provider: SecretsProvider) -> None:
        self.providers.append(provider)

    def get(self, key: str, *, default: str | None = None) -> str | None:
        for provider in self.providers:
            value = provider.get(key)
            if value is not None:
                return value
        return default
