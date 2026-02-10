# Installation

## Requirements

- Python 3.10+
- pip
- Rust toolchain (only required for source builds)

## Install from PyPI

```bash
pip install vyro
```

## Verify installation

Primary (recommended for end users):

```bash
vyro --help
```

Fallback (if your shell PATH does not expose `vyro` yet):

```bash
python -m vyro --help
```

## Why two commands?

- `vyro` is the official end-user CLI command.
- `python -m vyro` runs the same CLI module directly and is useful for PATH/debug scenarios.

## PATH troubleshooting

If `vyro` is not found:

1. Re-open terminal after install.
2. Ensure Python Scripts directory is on PATH.
3. Use `python -m vyro` temporarily.

## Developer setup

```bash
pip install -e .[dev]
pip install -e .[docs]
```
