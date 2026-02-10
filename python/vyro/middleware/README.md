# middleware

## Purpose
Middleware contracts and ordering pipeline for request/response hooks.

## Owns
- Base middleware interface.
- Registry and optimized execution chain (precompiled hooks).
- Priority-based middleware ordering rules.

## Entry Points
- `Middleware`
- `MiddlewareRegistry`

## Not Here
- Route parsing and native bridge calls.
