from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


ROUTE_DECORATORS = {"get", "post", "put", "delete"}


@dataclass(slots=True)
class LintIssue:
    path: str
    line: int
    message: str


def lint_source(path: Path, source: str) -> list[LintIssue]:
    tree = ast.parse(source, filename=str(path))
    issues: list[LintIssue] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and _has_route_decorator(node):
            issues.append(
                LintIssue(
                    path=str(path),
                    line=node.lineno,
                    message=f"route handler '{node.name}' must be declared with async def",
                )
            )
            continue

        if isinstance(node, ast.AsyncFunctionDef) and _has_route_decorator(node):
            if not node.args.args:
                issues.append(
                    LintIssue(
                        path=str(path),
                        line=node.lineno,
                        message=f"route handler '{node.name}' must accept first argument 'ctx'",
                    )
                )
                continue
            if node.args.args[0].arg != "ctx":
                issues.append(
                    LintIssue(
                        path=str(path),
                        line=node.lineno,
                        message=f"route handler '{node.name}' first argument must be 'ctx'",
                    )
                )
    return issues


def lint_project(root: Path) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for path in root.rglob("*.py"):
        if any(part.startswith(".") for part in path.parts):
            continue
        source = path.read_text(encoding="utf-8")
        issues.extend(lint_source(path, source))
    return issues


def _has_route_decorator(node: ast.AsyncFunctionDef | ast.FunctionDef) -> bool:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call):
            target = decorator.func
        else:
            target = decorator
        if isinstance(target, ast.Attribute) and target.attr in ROUTE_DECORATORS:
            return True
    return False
