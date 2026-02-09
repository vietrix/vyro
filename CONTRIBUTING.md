# Contributing to Vyro

Thank you for contributing to Vyro.

## Scope

We welcome:
- Bug fixes
- Performance improvements
- Documentation improvements
- Tests and CI hardening
- New features aligned with the project roadmap

## Prerequisites

- Python 3.10+
- Rust stable toolchain
- `maturin`
- `pytest`

## Setup

```bash
pip install -U pip
pip install maturin pytest
```

## Development Workflow

1. Fork the repository and create a branch from `main`.
2. Keep changes focused (one logical concern per pull request).
3. Add or update tests for behavioral changes.
4. Update docs when public behavior or developer workflow changes.
5. Run all required checks before opening a PR.

## Required Checks

```bash
cargo test
python -m pytest tests/py tests/integration -q
maturin build --release
```

## Commit Conventions

Use Conventional Commits:
- `feat: ...`
- `fix: ...`
- `refactor: ...`
- `docs: ...`
- `test: ...`
- `chore: ...`

For breaking changes, add a clear marker in the commit body.

## Pull Request Checklist

- [ ] Branch is up to date with `main`
- [ ] Tests pass locally
- [ ] Docs are updated (if applicable)
- [ ] No unrelated file churn
- [ ] Commit messages follow Conventional Commits

## Review Expectations

- Maintainers prioritize correctness, performance, and maintainability.
- Expect direct technical feedback and requested changes when needed.
- Please respond to review comments in the same PR thread.

## Release Notes Guidance

Release notes are generated from Conventional Commits. Use clear, user-facing summaries in commit subjects to improve changelog quality.

## Code of Conduct

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
