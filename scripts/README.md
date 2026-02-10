# scripts

## Purpose
Automation scripts used by CI and release workflows.

## Owns
- Release notes and changelog generation.
- Tag/version parsing for release jobs.
- Developer automation scripts (`scripts.dev.*`) for toolchain checks/tests/build/bench.

## Entry Points
- `python -m scripts.release.release notes ...`
- `python -m scripts.dev.check`
- `python -m scripts.dev.test`
- `python -m scripts.dev.build --sdist`
- `python -m scripts.dev.bench --suite all --iterations 5000 --out benchmark.current.json`

## Not Here
- Runtime server logic.
