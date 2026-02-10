from __future__ import annotations

from vyro import Context, Vyro
from vyro.runtime.tenant_routing import TenantRoutingConfig


def test_tenant_route_prefix_is_added() -> None:
    app = Vyro()

    @app.get("/users/:id", tenant="acme")
    async def get_user(ctx: Context, id: int):  # type: ignore[no-untyped-def]
        return {"id": id}

    record = app._router.records()[0]  # noqa: SLF001
    assert record.tenant == "acme"
    assert record.normalized_path == "/tenants/acme/users/{id}"


def test_tenant_route_with_version_prefix() -> None:
    app = Vyro()

    @app.get("/orders/:id", tenant="globex", version="2")
    async def get_order(ctx: Context, id: int):  # type: ignore[no-untyped-def]
        return {"id": id}

    record = app._router.records()[0]  # noqa: SLF001
    assert record.version == "/v2"
    assert record.tenant == "globex"
    assert record.normalized_path == "/v2/tenants/globex/orders/{id}"


def test_tenant_route_respects_alias_config() -> None:
    app = Vyro()
    app.set_tenant_routing_config(
        TenantRoutingConfig(prefix_template="/orgs/{tenant_id}", aliases={"vtx": "vietrix"})
    )

    @app.get("/health", tenant="vtx")
    async def health(ctx: Context):  # type: ignore[no-untyped-def]
        return {"ok": True}

    record = app._router.records()[0]  # noqa: SLF001
    assert record.tenant == "vietrix"
    assert record.normalized_path == "/orgs/vietrix/health"
