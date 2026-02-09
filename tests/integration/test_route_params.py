from vyro.routing.normalize import normalize_path


def test_route_params_normalization() -> None:
    assert normalize_path("/users/:id") == "/users/{id}"
