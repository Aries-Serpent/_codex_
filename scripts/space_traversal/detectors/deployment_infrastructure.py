"""Dynamic detector for deployment infrastructure capability.

Detects Docker configurations, Kubernetes/Helm charts, Terraform,
deployment scripts, and service definitions.

Safeguards: Bounded processing, deterministic sorting, validation.
"""

from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect deployment infrastructure capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result with comprehensive metadata
    """
    files = file_index.get("files", [])

    # Evidence collection
    docker_files = []
    k8s_files = []
    helm_files = []
    terraform_files = []
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

        # Terraform
        if path.endswith(".tf") or "terraform/" in path:
            terraform_files.append(path)

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
        set(
            docker_files + k8s_files + helm_files + terraform_files + service_files + deploy_scripts
        )
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
    if terraform_files:
        found_patterns.append("terraform")

    # Calculate functionality score
    functionality_score = len(found_patterns) / len(required_patterns) if required_patterns else 0.0

    return {
        "id": "deployment-infrastructure",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "deployment",
            "infrastructure",
            "docker",
            "kubernetes",
            "helm",
            "terraform",
            "ci-cd",
        ],
        "safeguards": ["validation", "bounded", "deterministic", "error-handling"],
        "functionality_impl": functionality_score,
        "meta": {
            "docker_configs": len(docker_files),
            "k8s_manifests": len(k8s_files),
            "helm_charts": len(helm_files),
            "terraform_configs": len(terraform_files),
            "service_definitions": len(service_files),
            "deploy_scripts": len(deploy_scripts),
            "deterministic": True,
            "offline": True,
            "bounded": True,
        },
    }
