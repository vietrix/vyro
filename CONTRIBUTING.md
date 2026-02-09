# Contributing

## Principles
- Keep public API stable: `from vyro import App, Context`.
- Prefer small focused modules over generic utility files.
- Keep Rust/Python boundaries explicit.

## Local Checks
- `cargo test`
- `python -m pytest tests/py -q`
- `maturin build --release`

## Commit Style
- Use Conventional Commits (`feat:`, `fix:`, `refactor:`, ...).
