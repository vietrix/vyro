from __future__ import annotations

from vyro.api.openapi_compat import compare_openapi


def test_openapi_compat_detects_removed_path() -> None:
    base = {
        "openapi": "3.1.0",
        "paths": {
            "/users/{id}": {
                "get": {
                    "parameters": [],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    target = {"openapi": "3.1.0", "paths": {}}
    issues = compare_openapi(base, target)
    assert issues
    assert issues[0].message == "path removed"


def test_openapi_compat_detects_required_upgrade() -> None:
    base = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {"name": "q", "in": "query", "required": False, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    target = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    issues = compare_openapi(base, target)
    assert any("became required" in issue.message for issue in issues)


def test_openapi_compat_passes_for_backward_compatible_changes() -> None:
    base = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {"name": "limit", "in": "query", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    target = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}},
                        {"name": "offset", "in": "query", "required": False, "schema": {"type": "integer"}},
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    issues = compare_openapi(base, target)
    assert issues == []
