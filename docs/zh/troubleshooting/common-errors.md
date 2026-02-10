# Troubleshooting

## `Invalid --app format`

Use `<module>:<attribute>`, for example `examples.hello_world:app`.

## Route signature errors

Ensure handlers are `async def` and first arg is `ctx`.

## Native build issues

Install Rust toolchain and rebuild with `maturin build --release`.

## Docs build errors

Run `mkdocs build --strict` and fix broken links or missing pages.
