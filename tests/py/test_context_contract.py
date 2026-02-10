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


def test_context_core_views_are_immutable() -> None:
    ctx = Context.from_native(
        {
            "headers": {"user-agent": "pytest"},
            "query": {"q": "ok"},
            "path_params": {"id": "1"},
            "body": b"",
        }
    )
    try:
        ctx.headers["x"] = "1"  # type: ignore[index]
        raised = False
    except TypeError:
        raised = True
    assert raised is True


def test_context_extensions_are_mutable() -> None:
    ctx = Context.from_native(
        {
            "headers": {},
            "query": {},
            "path_params": {},
            "body": b"",
        }
    )
    ctx.set_extension("trace_id", "abc123")
    assert ctx.get_extension("trace_id") == "abc123"
    assert ctx.extensions["trace_id"] == "abc123"
