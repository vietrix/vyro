from vyro.http.context import Context


def test_context_from_native() -> None:
    ctx = Context.from_native(
        {
            "headers": {"user-agent": "pytest"},
            "query": {"q": "ok"},
            "path_params": {"id": "1"},
            "body": b'{"x":1}',
        }
    )
    assert ctx.headers["user-agent"] == "pytest"
    assert ctx.query["q"] == "ok"
    assert ctx.path_params["id"] == "1"
    assert ctx.body_bytes() == b'{"x":1}'
