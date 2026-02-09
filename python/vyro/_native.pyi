from typing import Any, Callable

def start_server(
    host: str,
    port: int,
    workers: int,
    routes: list[tuple[str, str, Callable[[dict[str, Any]], Any]]],
) -> None: ...
