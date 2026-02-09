import inspect

from vyro.routing.signature import bind_path_kwargs


def test_bind_path_kwargs_with_int_cast() -> None:
    def handler(ctx, id: int):  # type: ignore[no-untyped-def]
        return id

    params = list(inspect.signature(handler).parameters.values())
    kwargs = bind_path_kwargs("handler", params, {"id": "42"})
    assert kwargs["id"] == 42
