from __future__ import annotations

from vyro.errors import RouteDefinitionError


def normalize_path(path: str) -> str:
    if not path:
        raise RouteDefinitionError("Route path cannot be empty.")
    if not path.startswith("/"):
        raise RouteDefinitionError("Route path must start with '/'.")
    if path == "/":
        return path

    segments = path.split("/")
    normalized_segments: list[str] = []
    used_names: set[str] = set()
    wildcard_seen = False

    for idx, seg in enumerate(segments):
        if idx == 0:
            continue
        if not seg:
            raise RouteDefinitionError(f"Route path contains empty segment: '{path}'")
        if seg.startswith(":"):
            name = seg[1:]
            if not name:
                raise RouteDefinitionError(f"Invalid parameter segment: '{seg}'")
            if wildcard_seen:
                raise RouteDefinitionError("No segment is allowed after wildcard.")
            if name in used_names:
                raise RouteDefinitionError(f"Duplicate path parameter name '{name}'")
            used_names.add(name)
            normalized_segments.append(f"{{{name}}}")
            continue
        if seg == "*":
            if wildcard_seen:
                raise RouteDefinitionError("Only one wildcard segment is allowed.")
            wildcard_seen = True
            name = "wildcard"
            if name in used_names:
                suffix = 1
                while f"wildcard_{suffix}" in used_names:
                    suffix += 1
                name = f"wildcard_{suffix}"
            used_names.add(name)
            normalized_segments.append(f"{{*{name}}}")
            continue
        if seg.startswith("*"):
            if wildcard_seen:
                raise RouteDefinitionError("Only one wildcard segment is allowed.")
            name = seg[1:] or "wildcard"
            if name in used_names:
                raise RouteDefinitionError(f"Duplicate wildcard parameter name '{name}'")
            wildcard_seen = True
            used_names.add(name)
            normalized_segments.append(f"{{*{name}}}")
            continue
        if wildcard_seen:
            raise RouteDefinitionError("No segment is allowed after wildcard.")
        normalized_segments.append(seg)

    return "/" + "/".join(normalized_segments)
