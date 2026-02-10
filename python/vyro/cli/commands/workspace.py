from __future__ import annotations

from pathlib import Path

import typer

from vyro.cli.runtime import error, info, warn

app = typer.Typer(help="Monorepo workspace commands.")

WORKSPACE_FILE = "vyro.workspace.toml"


@app.command("init")
def init_workspace(
    name: str = typer.Argument("workspace", help="Workspace directory name."),
    apps: str = typer.Option("api", "--apps", help="Comma-separated app packages."),
    libs: str = typer.Option("common", "--libs", help="Comma-separated shared libraries."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files when needed."),
) -> None:
    root = Path(name)
    root.mkdir(parents=True, exist_ok=True)

    apps_list = _parse_csv(apps, fallback="api")
    libs_list = _parse_csv(libs, fallback="common")

    apps_dir = root / "apps"
    libs_dir = root / "libs"
    apps_dir.mkdir(parents=True, exist_ok=True)
    libs_dir.mkdir(parents=True, exist_ok=True)

    for app_name in apps_list:
        app_dir = apps_dir / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        app_py = app_dir / "app.py"
        if app_py.exists() and not force:
            continue
        app_py.write_text(
            "\n".join(
                [
                    "from vyro import Context, Vyro",
                    "",
                    "app = Vyro()",
                    "",
                    '@app.get("/")',
                    "async def health(ctx: Context):",
                    f'    return {{"service": "{app_name}", "status": "ok"}}',
                    "",
                    'if __name__ == "__main__":',
                    "    app.run(port=8000, workers=1)",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    for lib_name in libs_list:
        lib_dir = libs_dir / lib_name
        lib_dir.mkdir(parents=True, exist_ok=True)
        init_py = lib_dir / "__init__.py"
        if init_py.exists() and not force:
            continue
        init_py.write_text(
            f'"""Shared library package: {lib_name}."""\n',
            encoding="utf-8",
        )

    workspace_toml = root / WORKSPACE_FILE
    if not workspace_toml.exists() or force:
        apps_members = ", ".join(f'"apps/{item}"' for item in apps_list)
        libs_members = ", ".join(f'"libs/{item}"' for item in libs_list)
        workspace_toml.write_text(
            "\n".join(
                [
                    '[workspace]',
                    f'name = "{root.name}"',
                    "",
                    "[workspace.members]",
                    f"apps = [{apps_members}]",
                    f"libs = [{libs_members}]",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    readme = root / "README.md"
    if not readme.exists() or force:
        readme.write_text(
            "\n".join(
                [
                    f"# {root.name}",
                    "",
                    "Vyro monorepo workspace.",
                    "",
                    "## Layout",
                    "- `apps/`: deployable services",
                    "- `libs/`: shared domain libraries",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    info(
        f"Workspace initialized at '{root}' with apps={len(apps_list)} libs={len(libs_list)}."
    )


@app.command("status")
def workspace_status(
    root: Path = typer.Option(Path("."), "--root", help="Workspace root path."),
    strict: bool = typer.Option(False, "--strict/--no-strict", help="Return non-zero when invalid."),
) -> None:
    workspace_file = root / WORKSPACE_FILE
    if not workspace_file.exists():
        message = f"workspace file not found: {workspace_file}"
        if strict:
            error(message)
            raise typer.Exit(code=1)
        warn(message)
        return

    apps_dir = root / "apps"
    libs_dir = root / "libs"
    apps = [path.name for path in apps_dir.iterdir() if path.is_dir()] if apps_dir.exists() else []
    libs = [path.name for path in libs_dir.iterdir() if path.is_dir()] if libs_dir.exists() else []

    info(f"workspace: {root.resolve()}")
    info(f"workspace apps: {len(apps)} ({', '.join(sorted(apps)) if apps else 'none'})")
    info(f"workspace libs: {len(libs)} ({', '.join(sorted(libs)) if libs else 'none'})")


def _parse_csv(value: str, *, fallback: str) -> list[str]:
    items = [item.strip().replace("-", "_") for item in value.split(",") if item.strip()]
    if not items:
        return [fallback]
    return [item for item in items if item]
