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


def test_context_injects_correlation_id_when_missing() -> None:
    ctx = Context.from_native(
        {
            "headers": {"user-agent": "pytest"},
            "query": {},
            "path_params": {},
            "body": b"",
        }
    )
    assert "x-correlation-id" in ctx.headers
    assert ctx.correlation_id == ctx.headers["x-correlation-id"]


def test_context_uses_incoming_correlation_id() -> None:
    ctx = Context.from_native(
        {
            "headers": {"x-correlation-id": "abc-123"},
            "query": {},
            "path_params": {},
            "body": b"",
        }
    )
    assert ctx.correlation_id == "abc-123"


def test_context_injects_traceparent_when_missing() -> None:
    ctx = Context.from_native(
        {
            "headers": {"x-correlation-id": "abc-123"},
            "query": {},
            "path_params": {},
            "body": b"",
        }
    )
    assert "traceparent" in ctx.headers
    assert ctx.traceparent.startswith("00-")


def test_context_uses_incoming_traceparent() -> None:
    value = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    ctx = Context.from_native(
        {
            "headers": {"traceparent": value},
            "query": {},
            "path_params": {},
            "body": b"",
        }
    )
    assert ctx.traceparent == value
