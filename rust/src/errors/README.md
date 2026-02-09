# errors

## Purpose
Error model for Rust engine and Python error conversion.

## Owns
- Core runtime errors.
- Mapping from `CoreError` to Python exceptions.

## Entry Points
- `core_error::CoreError`
- `py_error::to_py_runtime`

## Not Here
- HTTP status response rendering.
