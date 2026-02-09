# routing

## Purpose
Route declaration pipeline from decorator input to native route table.

## Owns
- DSL normalization and validation.
- Handler signature checks.
- Dispatch wrapper that builds `Context` and kwargs.

## Entry Points
- `RouterRegistry.add_route`
- `normalize_path`

## Not Here
- HTTP server and network runtime.
