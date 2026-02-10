from __future__ import annotations

from pathlib import Path

import typer

from vyro.benchmarks.gate import compare_benchmarks, load_benchmark_file


def main(
    baseline: Path = typer.Option(..., "--baseline", exists=True, file_okay=True, dir_okay=False),
    current: Path = typer.Option(..., "--current", exists=True, file_okay=True, dir_okay=False),
    threshold_percent: float = typer.Option(50.0, "--threshold-percent"),
) -> None:
    baseline_payload = load_benchmark_file(baseline)
    current_payload = load_benchmark_file(current)
    regressions = compare_benchmarks(
        baseline_payload,
        current_payload,
        threshold_percent=threshold_percent,
    )
    if regressions:
        for item in regressions:
            typer.echo(
                f"ERROR: regression suite={item.suite} baseline={item.baseline_us_per_op:.3f}us "
                f"current={item.current_us_per_op:.3f}us delta={item.delta_percent:.2f}%"
            )
        raise typer.Exit(code=1)
    typer.echo("INFO: benchmark regression gate passed")


if __name__ == "__main__":
    typer.run(main)
