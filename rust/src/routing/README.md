# routing

## Purpose
Route storage and request path lookup for native engine.

## Owns
- Route definition structs.
- Method-based route table.
- Path parameter extraction output.

## Entry Points
- `RouteRegistry::from_routes`
- `RouteRegistry::lookup`

## Not Here
- Hyper server loop and response encoding.
