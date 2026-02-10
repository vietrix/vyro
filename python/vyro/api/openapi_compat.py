from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CompatibilityIssue:
    path: str
    method: str
    message: str


def load_openapi_document(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_openapi(base: dict[str, Any], target: dict[str, Any]) -> list[CompatibilityIssue]:
    issues: list[CompatibilityIssue] = []
    base_paths: dict[str, Any] = base.get("paths", {})
    target_paths: dict[str, Any] = target.get("paths", {})

    for path, base_ops in base_paths.items():
        if path not in target_paths:
            issues.append(CompatibilityIssue(path=path, method="*", message="path removed"))
            continue
        target_ops = target_paths[path]
        for method, base_op in base_ops.items():
            if method not in target_ops:
                issues.append(CompatibilityIssue(path=path, method=method, message="operation removed"))
                continue
            issues.extend(_compare_operation(path, method, base_op, target_ops[method]))
    return issues


def _compare_operation(
    path: str,
    method: str,
    base_op: dict[str, Any],
    target_op: dict[str, Any],
) -> list[CompatibilityIssue]:
    issues: list[CompatibilityIssue] = []
    base_params = {f"{p['in']}:{p['name']}": p for p in base_op.get("parameters", [])}
    target_params = {f"{p['in']}:{p['name']}": p for p in target_op.get("parameters", [])}

    for key, param in base_params.items():
        if key not in target_params:
            issues.append(
                CompatibilityIssue(path=path, method=method, message=f"parameter removed: {key}")
            )
            continue
        t_param = target_params[key]
        if bool(param.get("required")) and not bool(t_param.get("required")):
            # required -> optional is backward compatible
            pass
        elif not bool(param.get("required")) and bool(t_param.get("required")):
            issues.append(
                CompatibilityIssue(
                    path=path,
                    method=method,
                    message=f"parameter became required: {key}",
                )
            )
        base_schema = param.get("schema", {})
        target_schema = t_param.get("schema", {})
        if base_schema.get("type") != target_schema.get("type"):
            issues.append(
                CompatibilityIssue(
                    path=path,
                    method=method,
                    message=f"parameter type changed for {key}: {base_schema.get('type')} -> {target_schema.get('type')}",
                )
            )
        if base_schema.get("format") != target_schema.get("format"):
            issues.append(
                CompatibilityIssue(
                    path=path,
                    method=method,
                    message=f"parameter format changed for {key}: {base_schema.get('format')} -> {target_schema.get('format')}",
                )
            )

    return issues
