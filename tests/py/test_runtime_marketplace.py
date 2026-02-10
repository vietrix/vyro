from __future__ import annotations

import json

import pytest

from vyro.runtime.marketplace import ExtensionManifest, ExtensionMarketplaceManifest, ManifestError


def test_manifest_from_dict_accepts_valid_payload() -> None:
    manifest = ExtensionManifest.from_dict(
        {
            "name": "vyro-observability",
            "version": "0.1.0",
            "abi_version": "1.0",
            "module": "vyro_ext.observability",
            "summary": "Tracing integrations",
            "keywords": ["otel", "metrics"],
        }
    )
    assert manifest.name == "vyro-observability"
    assert manifest.keywords == ("otel", "metrics")


def test_manifest_rejects_missing_required_fields() -> None:
    with pytest.raises(ManifestError, match="missing required fields"):
        ExtensionManifest.from_dict({"name": "x", "version": "0.1.0"})


def test_manifest_rejects_abi_mismatch() -> None:
    with pytest.raises(ManifestError, match="ABI mismatch"):
        ExtensionManifest.from_dict(
            {
                "name": "plugin-bad",
                "version": "0.1.0",
                "abi_version": "2.0",
                "module": "plugin.bad",
            }
        )


def test_marketplace_register_and_lookup() -> None:
    marketplace = ExtensionMarketplaceManifest()
    manifest = marketplace.register_from_dict(
        {
            "name": "vyro-cachex",
            "version": "1.2.0",
            "abi_version": "1.0",
            "module": "vyro_ext.cachex",
        }
    )
    assert marketplace.get("vyro-cachex") == manifest
    assert len(marketplace.all()) == 1


def test_manifest_from_json_text_invalid_payload() -> None:
    with pytest.raises(ManifestError, match="invalid manifest JSON"):
        ExtensionManifest.from_json_text("{bad json")

    with pytest.raises(ManifestError, match="root must be an object"):
        ExtensionManifest.from_json_text(json.dumps(["not", "object"]))
