# python

## Purpose
Developer-facing API layer for vyro.

## Owns
- Route declaration and validation.
- Context and middleware contracts.
- Thin bridge invocation to native Rust module.
- Handler contract enforcement (`async def`, first arg is `ctx`).
- Typed scalar coercion for request bindings (path/query/header).

## Entry Points
- `vyro.Vyro`
- `vyro.Context`

## Not Here
- Network loop and routing execution internals.
