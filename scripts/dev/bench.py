from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path


def run(suite: str, iterations: int, out: Path | None) -> int:
    if iterations < 1:
        print("ERROR: --iterations must be >= 1")
        return 2

    selected = suite.strip().lower()
    allowed = {"routing", "json", "latency", "all"}
    if selected not in allowed:
        print("ERROR: --suite must be one of routing|json|latency|all")
        return 2

    benches = []
    if selected in {"routing", "all"}:
        benches.append(("routing", _bench_routing))
    if selected in {"json", "all"}:
        benches.append(("json", _bench_json))
    if selected in {"latency", "all"}:
        benches.append(("latency", _bench_latency))

    results: dict[str, dict[str, float | int]] = {}
    for name, fn in benches:
        duration_sec = fn(iterations)
        ops_per_sec = iterations / duration_sec if duration_sec > 0 else float("inf")
        us_per_op = (duration_sec * 1_000_000) / iterations
        results[name] = {
            "iterations": iterations,
            "duration_sec": round(duration_sec, 6),
            "ops_per_sec": round(ops_per_sec, 2),
            "us_per_op": round(us_per_op, 3),
        }
        print(
            "INFO: "
            f"bench[{name}] iterations={iterations} duration={duration_sec:.6f}s "
            f"ops_per_sec={ops_per_sec:.2f} us_per_op={us_per_op:.3f}"
        )

    payload = {"suite": selected, "results": results}
    if out is not None:
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"INFO: benchmark result written to '{out}'")
    else:
        print(json.dumps(payload, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Developer benchmark helper.")
    parser.add_argument("--suite", default="all")
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    out = Path(args.out) if args.out else None
    return run(suite=args.suite, iterations=args.iterations, out=out)


def _bench_routing(iterations: int) -> float:
    from vyro.routing.normalize import normalize_path

    samples = ["/users/:id", "/static/*", "/v1/orders/:order_id/items/:item_id", "/health"]
    start = time.perf_counter()
    for i in range(iterations):
        normalize_path(samples[i % len(samples)])
    return time.perf_counter() - start


def _bench_json(iterations: int) -> float:
    payload = {"id": 1, "name": "vyro", "tags": ["rust", "python", "api"], "nested": {"ok": True}}
    start = time.perf_counter()
    for _ in range(iterations):
        encoded = json.dumps(payload, separators=(",", ":"))
        json.loads(encoded)
    return time.perf_counter() - start


def _bench_latency(iterations: int) -> float:
    samples: list[float] = []
    for i in range(iterations):
        t0 = time.perf_counter_ns()
        _ = (i * 3) ^ (i >> 1)
        t1 = time.perf_counter_ns()
        samples.append(float(t1 - t0))
    mean_ns = statistics.fmean(samples) if samples else 0.0
    total_sec = (mean_ns * iterations) / 1_000_000_000
    return total_sec


if __name__ == "__main__":
    raise SystemExit(main())
