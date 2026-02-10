from __future__ import annotations

from vyro.runtime.kubernetes import KubernetesAppConfig, KubernetesManifestGenerator


def test_kubernetes_generator_renders_deployment_and_service() -> None:
    generator = KubernetesManifestGenerator()
    manifest = generator.generate(
        KubernetesAppConfig(
            name="vyro-api",
            image="ghcr.io/vietrix/vyro:latest",
            namespace="production",
            replicas=3,
            container_port=9000,
            service_port=80,
            workers=4,
            env={"VYRO_ENV": "production"},
        )
    )
    assert "kind: Deployment" in manifest
    assert "kind: Service" in manifest
    assert "name: vyro-api" in manifest
    assert "namespace: production" in manifest
    assert "containerPort: 9000" in manifest
    assert "port: 80" in manifest
    assert "name: VYRO_WORKERS" in manifest
