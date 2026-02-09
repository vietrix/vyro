from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.release.versioning import parse_tag


def test_parse_release_tag_formats() -> None:
    stable = parse_tag("v1.2.3")
    rc = parse_tag("v1.2.3-rc.1")
    assert stable.python_version == "1.2.3"
    assert rc.python_version == "1.2.3rc1"
