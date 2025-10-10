"""Dynamic detector for deployment infrastructure capability.

Detects Docker configurations, Kubernetes/Helm charts, deployment
scripts, and service definitions.
"""
from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect deployment infrastructure capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    docker_files = []
    k8s_files = []
    helm_files = []
    service_files = []
    deploy_scripts = []

    for f in files:
        path = f["path"]

        # Docker
        if any(
            name in path
            for name in [
                "Dockerfile",
                "docker-compose.yml",
                ".dockerignore",
                "docker/",
            ]
        ):
            docker_files.append(path)

        # Kubernetes
        if any(
            kw in path.lower() for kw in ["k8s/", "kubernetes/", "deployment.yaml", "service.yaml"]
        ):
            k8s_files.append(path)

        # Helm
        if "helm/" in path or "Chart.yaml" in path or "values.yaml" in path:
            helm_files.append(path)

        # Service definitions
        if path.startswith("services/") or "api/" in path:
            service_files.append(path)

        # Deployment scripts
        if path.startswith("scripts/deploy/") or "deploy" in path.lower() and path.endswith(".sh"):
            deploy_scripts.append(path)

    # Pattern detection
    found_patterns = []
    required_patterns = ["docker", "kubernetes", "helm", "deploy", "service"]

    evidence_files = sorted(
        set(docker_files + k8s_files + helm_files + service_files + deploy_scripts)
    )

    if docker_files:
        found_patterns.append("docker")
    if k8s_files:
        found_patterns.append("kubernetes")
    if helm_files:
        found_patterns.append("helm")
    if deploy_scripts:
        found_patterns.append("deploy")
    if service_files:
        found_patterns.append("service")

    return {
        "id": "deployment-infrastructure",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {
            "docker_configs": len(docker_files),
            "k8s_manifests": len(k8s_files),
            "helm_charts": len(helm_files),
            "service_definitions": len(service_files),
            "deploy_scripts": len(deploy_scripts),
        },
    }
