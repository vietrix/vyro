from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .plugins import ABI_VERSION


class ManifestError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ExtensionManifest:
    name: str
    version: str
    abi_version: str
    module: str
    summary: str = ""
    homepage: str | None = None
    keywords: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExtensionManifest":
        required = ("name", "version", "abi_version", "module")
        missing = [key for key in required if key not in data or not str(data[key]).strip()]
        if missing:
            raise ManifestError(f"manifest is missing required fields: {', '.join(missing)}")

        abi_version = str(data["abi_version"])
        if abi_version != ABI_VERSION:
            raise ManifestError(f"manifest ABI mismatch: {abi_version} (expected {ABI_VERSION})")

        raw_keywords = data.get("keywords", [])
        if raw_keywords is None:
            raw_keywords = []
        if not isinstance(raw_keywords, list):
            raise ManifestError("keywords must be a list of strings")
        keywords = tuple(str(item).strip() for item in raw_keywords if str(item).strip())

        homepage_raw = data.get("homepage")
        homepage = str(homepage_raw) if homepage_raw else None

        return cls(
            name=str(data["name"]).strip(),
            version=str(data["version"]).strip(),
            abi_version=abi_version,
            module=str(data["module"]).strip(),
            summary=str(data.get("summary", "")).strip(),
            homepage=homepage,
            keywords=keywords,
        )

    @classmethod
    def from_json_text(cls, text: str) -> "ExtensionManifest":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ManifestError(f"invalid manifest JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ManifestError("manifest root must be an object")
        return cls.from_dict(payload)

    @classmethod
    def from_file(cls, path: Path) -> "ExtensionManifest":
        return cls.from_json_text(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class ExtensionMarketplaceManifest:
    _manifests: dict[str, ExtensionManifest] = field(default_factory=dict)

    def register(self, manifest: ExtensionManifest) -> None:
        self._manifests[manifest.name] = manifest

    def register_from_dict(self, data: dict[str, Any]) -> ExtensionManifest:
        manifest = ExtensionManifest.from_dict(data)
        self.register(manifest)
        return manifest

    def register_from_file(self, path: Path) -> ExtensionManifest:
        manifest = ExtensionManifest.from_file(path)
        self.register(manifest)
        return manifest

    def get(self, name: str) -> ExtensionManifest | None:
        return self._manifests.get(name)

    def all(self) -> tuple[ExtensionManifest, ...]:
        return tuple(sorted(self._manifests.values(), key=lambda item: item.name))
