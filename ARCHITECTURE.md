# vyro Architecture

## Purpose
vyro separates developer-facing Python APIs from the Rust execution engine.

## Layers
- Python API: route declarations, context wrappers, middleware contracts.
- Rust Engine: runtime, HTTP serving, route matching, callback bridging.
- Release Automation: Python scripts for changelog and release notes.

## Request Flow
1. User registers routes with `Vyro`.
2. `Vyro.run()` compiles a deterministic route plan (AOT bootstrap) and exports it to Rust.
3. Rust server matches request with `matchit`.
4. Python dispatch binds typed args from path/query/headers, then executes async handler.
5. Rust maps handler output back to HTTP response.

## Folder Rules
- Feature folders own one concern only.
- Every feature folder includes a short `README.md`.
- Public Python API stays under `python/vyro`.
