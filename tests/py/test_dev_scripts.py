from __future__ import annotations

import json

from scripts.dev import bench


def test_dev_bench_writes_result_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    out_file = tmp_path / "bench.json"
    exit_code = bench.run(suite="routing", iterations=100, out=out_file)
    assert exit_code == 0
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["suite"] == "routing"
    assert "routing" in payload["results"]


def test_dev_bench_rejects_invalid_suite() -> None:
    exit_code = bench.run(suite="invalid", iterations=100, out=None)
    assert exit_code == 2
