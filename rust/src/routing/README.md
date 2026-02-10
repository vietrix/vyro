# routing

## Purpose
Route storage and request path lookup for native engine.

## Owns
- Route definition structs.
- Method-partitioned radix route table (normalized by HTTP method).
- Path parameter extraction output.

## Entry Points
- `RouteRegistry::from_routes`
- `RouteRegistry::lookup`

## Not Here
- Hyper server loop and response encoding.
