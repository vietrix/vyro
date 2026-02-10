from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class KubernetesAppConfig:
    name: str
    image: str
    namespace: str = "default"
    replicas: int = 2
    container_port: int = 8000
    service_port: int = 80
    workers: int = 2
    env: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class KubernetesManifestGenerator:
    def generate(self, config: KubernetesAppConfig) -> str:
        env_lines = [f"            - name: VYRO_WORKERS\n              value: \"{config.workers}\""]
        for key, value in sorted(config.env.items()):
            env_lines.append(f"            - name: {key}\n              value: \"{value}\"")
        env_block = "\n".join(env_lines)

        return (
            f"apiVersion: apps/v1\n"
            f"kind: Deployment\n"
            f"metadata:\n"
            f"  name: {config.name}\n"
            f"  namespace: {config.namespace}\n"
            f"spec:\n"
            f"  replicas: {max(1, config.replicas)}\n"
            f"  selector:\n"
            f"    matchLabels:\n"
            f"      app: {config.name}\n"
            f"  template:\n"
            f"    metadata:\n"
            f"      labels:\n"
            f"        app: {config.name}\n"
            f"    spec:\n"
            f"      containers:\n"
            f"        - name: {config.name}\n"
            f"          image: {config.image}\n"
            f"          ports:\n"
            f"            - containerPort: {config.container_port}\n"
            f"          env:\n"
            f"{env_block}\n"
            f"---\n"
            f"apiVersion: v1\n"
            f"kind: Service\n"
            f"metadata:\n"
            f"  name: {config.name}\n"
            f"  namespace: {config.namespace}\n"
            f"spec:\n"
            f"  selector:\n"
            f"    app: {config.name}\n"
            f"  ports:\n"
            f"    - protocol: TCP\n"
            f"      port: {config.service_port}\n"
            f"      targetPort: {config.container_port}\n"
            f"  type: ClusterIP\n"
        )
