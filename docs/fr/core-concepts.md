# Core Concepts

## Design model

- Python declares routes and handlers
- Rust executes networking/runtime work
- `Context` carries request metadata

## Handler rules

- Must be `async def`
- First arg must be `ctx`
- Additional typed args are bound from route/query

## Runtime ownership

`app.run()` starts the native runtime and worker model.
