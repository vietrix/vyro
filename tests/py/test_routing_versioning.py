from __future__ import annotations

from vyro import Context, Vyro


def test_route_version_prefix_with_numeric_version() -> None:
    app = Vyro()

    @app.get("/users/:id", version="1")
    async def get_user(ctx: Context, id: int):  # type: ignore[no-untyped-def]
        return {"id": id}

    record = app._router.records()[0]  # noqa: SLF001
    assert record.version == "/v1"
    assert record.normalized_path == "/v1/users/{id}"


def test_route_version_prefix_accepts_prefixed_value() -> None:
    app = Vyro()

    @app.get("/health", version="v2")
    async def health(ctx: Context):  # type: ignore[no-untyped-def]
        return {"ok": True}

    record = app._router.records()[0]  # noqa: SLF001
    assert record.version == "/v2"
    assert record.normalized_path == "/v2/health"


def test_route_deprecation_metadata_is_recorded() -> None:
    app = Vyro()

    @app.get("/legacy", deprecated="use /v2/legacy")
    async def legacy(ctx: Context):  # type: ignore[no-untyped-def]
        return {"ok": True}

    record = app._router.records()[0]  # noqa: SLF001
    assert record.deprecated == "use /v2/legacy"
