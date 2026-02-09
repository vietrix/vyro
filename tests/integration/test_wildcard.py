from vyro.routing.normalize import normalize_path


def test_wildcard_normalization() -> None:
    assert normalize_path("/assets/*") == "/assets/{*wildcard}"
