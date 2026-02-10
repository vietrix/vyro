# python

## Purpose
Developer-facing API layer for vyro.

## Owns
- Route declaration and validation.
- Context and middleware contracts.
- Thin bridge invocation to native Rust module.

## Entry Points
- `vyro.Vyro`
- `vyro.Context`

## Not Here
- Network loop and routing execution internals.
