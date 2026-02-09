import http


def test_http_status_constants() -> None:
    assert http.HTTPStatus.NOT_FOUND == 404
    assert http.HTTPStatus.METHOD_NOT_ALLOWED == 405
