from __future__ import annotations

import asyncio

import pytest

from vyro.runtime.edge.http_client import AsyncHttpClient, HttpResponse
from vyro.runtime.resilience.timeout_budget import TimeoutBudget


def test_async_http_client_returns_response_and_decodes_json(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AsyncHttpClient()

    def fake_send(request, timeout_sec):  # type: ignore[no-untyped-def]
        assert request.get_method() == "GET"
        assert timeout_sec == pytest.approx(2.0)
        return HttpResponse(status=200, headers={"content-type": "application/json"}, body=b'{"ok":true}')

    monkeypatch.setattr(AsyncHttpClient, "_send", staticmethod(fake_send))

    response = asyncio.run(client.get("https://example.com/health", timeout_sec=2.0))
    assert response.status == 200
    assert response.json() == {"ok": True}


def test_async_http_client_clamps_timeout_by_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AsyncHttpClient()
    now = [100.0]
    budget = TimeoutBudget(timeout_sec=5.0, _clock=lambda: now[0])
    now[0] = 102.0

    captured: dict[str, float | None] = {"timeout": None}

    def fake_send(request, timeout_sec):  # type: ignore[no-untyped-def]
        captured["timeout"] = timeout_sec
        return HttpResponse(status=204, headers={}, body=b"")

    monkeypatch.setattr(AsyncHttpClient, "_send", staticmethod(fake_send))

    asyncio.run(client.get("https://example.com/health", timeout_sec=10.0, budget=budget))
    assert captured["timeout"] == pytest.approx(3.0)


def test_async_http_client_fails_when_budget_expired() -> None:
    client = AsyncHttpClient()
    now = [10.0]
    budget = TimeoutBudget(timeout_sec=1.0, _clock=lambda: now[0])
    now[0] = 11.5
    with pytest.raises(TimeoutError, match="timeout budget expired"):
        asyncio.run(client.get("https://example.com/health", budget=budget))
