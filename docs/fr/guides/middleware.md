# Middleware

Register middleware with explicit order:

```python
app.add_middleware(my_middleware, priority=100)
```

## Recommendations

- Keep middleware pure and fast
- Use explicit priorities
- Keep IO-heavy work in runtime primitives

## Idempotency

Use idempotency middleware for write endpoints to avoid duplicate side effects.
