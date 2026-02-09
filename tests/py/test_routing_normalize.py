from vyro.routing.normalize import normalize_path


def test_normalize_path_param() -> None:
    assert normalize_path("/users/:id") == "/users/{id}"


def test_normalize_wildcard_default_name() -> None:
    assert normalize_path("/static/*") == "/static/{*wildcard}"


def test_normalize_wildcard_named() -> None:
    assert normalize_path("/static/*path") == "/static/{*path}"
