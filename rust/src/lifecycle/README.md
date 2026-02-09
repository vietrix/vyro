# lifecycle

## Purpose
Runtime bootstrap and process lifecycle boundaries.

## Owns
- Tokio runtime construction.
- Server startup orchestration.

## Entry Points
- `lifecycle::runtime::run`

## Not Here
- Request routing and response conversion logic.
