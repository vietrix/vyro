from __future__ import annotations

from vyro.runtime.security.secrets import EnvSecretsProvider, InMemorySecretsProvider, SecretsManager


def test_in_memory_secrets_provider_returns_value() -> None:
    provider = InMemorySecretsProvider(values={"db_password": "secret"})
    assert provider.get("db_password") == "secret"
    assert provider.get("missing") is None


def test_env_secrets_provider_reads_prefixed_variables(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("VYRO_SECRET_DB_PASSWORD", "p@ss")
    provider = EnvSecretsProvider()
    assert provider.get("db_password") == "p@ss"


def test_secrets_manager_uses_provider_order_with_default() -> None:
    manager = SecretsManager(
        providers=[
            InMemorySecretsProvider(values={"token": "first"}),
            InMemorySecretsProvider(values={"token": "second"}),
        ]
    )
    assert manager.get("token") == "first"
    assert manager.get("missing", default="fallback") == "fallback"
