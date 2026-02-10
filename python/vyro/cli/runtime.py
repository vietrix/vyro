from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import typer

from vyro.observability.logging import SamplingPolicy, emit_log
from vyro.vyro import Vyro


def _read_rate(env_name: str, default: float) -> float:
    raw = os.getenv(env_name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return min(1.0, max(0.0, value))


LOG_SAMPLING_POLICY = SamplingPolicy(
    info_rate=_read_rate("VYRO_LOG_SAMPLE_INFO", 1.0),
    warn_rate=_read_rate("VYRO_LOG_SAMPLE_WARN", 1.0),
    error_rate=_read_rate("VYRO_LOG_SAMPLE_ERROR", 1.0),
)


def info(message: str) -> None:
    emit_log("INFO", message, sampling_policy=LOG_SAMPLING_POLICY)


def warn(message: str) -> None:
    emit_log("WARN", message, sampling_policy=LOG_SAMPLING_POLICY)


def error(message: str) -> None:
    emit_log("ERROR", message, err=True, sampling_policy=LOG_SAMPLING_POLICY)


def run_command(command: list[str], *, cwd: Path | None = None) -> None:
    info(f"Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        raise typer.Exit(code=1)


def load_vyro_app(target: str) -> Vyro:
    if ":" not in target:
        error("Invalid --app format. Expected '<module>:<attribute>'.")
        raise typer.Exit(code=2)

    module_name, attr_name = target.split(":", maxsplit=1)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        error(f"Failed to import module '{module_name}': {exc}")
        raise typer.Exit(code=2) from exc

    try:
        value: Any = getattr(module, attr_name)
    except AttributeError as exc:
        error(f"Module '{module_name}' has no attribute '{attr_name}'.")
        raise typer.Exit(code=2) from exc

    if isinstance(value, Vyro):
        return value

    if callable(value):
        try:
            candidate = value()
        except TypeError as exc:
            error(f"Attribute '{attr_name}' is callable but requires arguments: {exc}")
            raise typer.Exit(code=2) from exc
        if isinstance(candidate, Vyro):
            return candidate
        error(
            f"Callable '{module_name}:{attr_name}' returned '{type(candidate).__name__}', expected Vyro."
        )
        raise typer.Exit(code=2)

    error(
        f"Attribute '{module_name}:{attr_name}' has type '{type(value).__name__}', expected Vyro or callable returning Vyro."
    )
    raise typer.Exit(code=2)


def get_version_string() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version

        pkg_version = version("vyro")
    except PackageNotFoundError:
        pkg_version = "local"

    try:
        commit = (
            subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                check=True,
                text=True,
                capture_output=True,
            )
            .stdout.strip()
        )
    except Exception:
        commit = "unknown"

    return f"{pkg_version} ({commit})"


def require_module(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def python_executable() -> str:
    return sys.executable
