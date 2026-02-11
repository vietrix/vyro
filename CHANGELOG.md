# Changelog

## Unreleased

### Breaking

- Replaced public app entrypoint `App()` with `Vyro()` (hard cut, no alias).

### Features

- Added official `vyro` CLI with `new`, `run`, `dev`, `check`, `test`, `build`, `version`, `doctor`, and `release notes` commands.
- Publish prebuilt wheels for Linux (x86_64/aarch64), macOS (x86_64/arm64), and Windows (x64) in the release pipeline so `pip` can install without local Rust builds.
- Recommend `pip install "vyro>=0.2.2" --only-binary=:all:` for production installs to force wheel usage from PyPI.
