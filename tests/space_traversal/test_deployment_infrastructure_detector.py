"""
Comprehensive tests for deployment-infrastructure detector.

Tests Docker, Kubernetes, Helm, Terraform detection and
deployment script recognition.
"""

import pytest
from scripts.space_traversal.detectors.deployment_infrastructure import detect


def test_deployment_infrastructure_no_files():
    """Test when no deployment files exist."""
    file_index = {
        "files": [
            {"path": "src/main.py", "ext": ".py"},
            {"path": "tests/test_main.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert result["evidence_files"] == []
    assert "found_patterns" in result


def test_deployment_infrastructure_dockerfile():
    """Test detection of Dockerfile."""
    file_index = {
        "files": [
            {"path": "Dockerfile", "ext": ""},
            {"path": "src/main.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "Dockerfile" in result["evidence_files"]
    assert "docker" in result["found_patterns"]
    assert result["meta"]["docker_configs"] == 1


def test_deployment_infrastructure_docker_compose():
    """Test detection of docker-compose files."""
    file_index = {
        "files": [
            {"path": "docker-compose.yml", "ext": ".yml"},
            {"path": "docker-compose.dev.yml", "ext": ".yml"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "docker" in result["found_patterns"]
    assert result["meta"]["docker_configs"] >= 1


def test_deployment_infrastructure_kubernetes():
    """Test detection of Kubernetes manifests."""
    file_index = {
        "files": [
            {"path": "k8s/deployment.yaml", "ext": ".yaml"},
            {"path": "k8s/service.yaml", "ext": ".yaml"},
            {"path": "kubernetes/ingress.yaml", "ext": ".yaml"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "kubernetes" in result["found_patterns"]
    assert result["meta"]["k8s_manifests"] == 3


def test_deployment_infrastructure_helm():
    """Test detection of Helm charts."""
    file_index = {
        "files": [
            {"path": "helm/Chart.yaml", "ext": ".yaml"},
            {"path": "helm/values.yaml", "ext": ".yaml"},
            {"path": "helm/templates/deployment.yaml", "ext": ".yaml"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "helm" in result["found_patterns"]
    assert result["meta"]["helm_charts"] >= 2


def test_deployment_infrastructure_terraform():
    """Test detection of Terraform files."""
    file_index = {
        "files": [
            {"path": "terraform/main.tf", "ext": ".tf"},
            {"path": "terraform/variables.tf", "ext": ".tf"},
            {"path": "infrastructure/aws.tf", "ext": ".tf"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "terraform" in result["found_patterns"]
    assert result["meta"]["terraform_configs"] == 3


def test_deployment_infrastructure_deploy_scripts():
    """Test detection of deployment scripts."""
    file_index = {
        "files": [
            {"path": "scripts/deploy/deploy.sh", "ext": ".sh"},
            {"path": "scripts/deploy.sh", "ext": ".sh"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "deploy" in result["found_patterns"]
    assert result["meta"]["deploy_scripts"] >= 1


def test_deployment_infrastructure_service_files():
    """Test detection of service definition files."""
    file_index = {
        "files": [
            {"path": "services/api/main.py", "ext": ".py"},
            {"path": "services/worker/worker.py", "ext": ".py"},
            {"path": "api/server.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "service" in result["found_patterns"]
    assert result["meta"]["service_definitions"] == 3


def test_deployment_infrastructure_comprehensive():
    """Test comprehensive deployment infrastructure."""
    file_index = {
        "files": [
            {"path": "Dockerfile", "ext": ""},
            {"path": "docker-compose.yml", "ext": ".yml"},
            {"path": "k8s/deployment.yaml", "ext": ".yaml"},
            {"path": "helm/Chart.yaml", "ext": ".yaml"},
            {"path": "terraform/main.tf", "ext": ".tf"},
            {"path": "scripts/deploy/deploy.sh", "ext": ".sh"},
            {"path": "services/api/main.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert len(result["evidence_files"]) >= 7
    assert "docker" in result["found_patterns"]
    assert "kubernetes" in result["found_patterns"]
    assert "helm" in result["found_patterns"]
    assert "terraform" in result["found_patterns"]
    assert "deploy" in result["found_patterns"]
    assert "service" in result["found_patterns"]


def test_deployment_infrastructure_required_patterns():
    """Test that required patterns are properly defined."""
    file_index = {"files": []}
    result = detect(file_index)

    assert "required_patterns" in result
    assert "docker" in result["required_patterns"]
    assert "kubernetes" in result["required_patterns"]
    assert "helm" in result["required_patterns"]


def test_deployment_infrastructure_docs_keywords():
    """Test that docs_keywords metadata is present."""
    file_index = {"files": []}
    result = detect(file_index)

    assert "docs_keywords" in result
    assert "deployment" in result["docs_keywords"]
    assert "docker" in result["docs_keywords"]
    assert "kubernetes" in result["docs_keywords"]


def test_deployment_infrastructure_safeguards():
    """Test that safeguards metadata is present."""
    file_index = {"files": []}
    result = detect(file_index)

    assert "safeguards" in result
    assert "validation" in result["safeguards"]
    assert "bounded" in result["safeguards"]
    assert "deterministic" in result["safeguards"]


def test_deployment_infrastructure_functionality():
    """Test that functionality score is calculated."""
    file_index = {
        "files": [
            {"path": "Dockerfile", "ext": ""},
            {"path": "k8s/deployment.yaml", "ext": ".yaml"},
        ]
    }
    result = detect(file_index)

    assert "functionality_impl" in result
    assert isinstance(result["functionality_impl"], float)
    assert 0.0 <= result["functionality_impl"] <= 1.0


def test_deployment_infrastructure_meta_fields():
    """Test that meta fields are properly populated."""
    file_index = {
        "files": [
            {"path": "Dockerfile", "ext": ""},
            {"path": "k8s/deployment.yaml", "ext": ".yaml"},
        ]
    }
    result = detect(file_index)

    assert "meta" in result
    assert "docker_configs" in result["meta"]
    assert "k8s_manifests" in result["meta"]
    assert "helm_charts" in result["meta"]
    assert "terraform_configs" in result["meta"]
    assert "service_definitions" in result["meta"]
    assert "deploy_scripts" in result["meta"]
    assert result["meta"]["deterministic"] is True


def test_deployment_infrastructure_sorted_evidence():
    """Test that evidence files are sorted deterministically."""
    file_index = {
        "files": [
            {"path": "k8s/z_deployment.yaml", "ext": ".yaml"},
            {"path": "k8s/a_service.yaml", "ext": ".yaml"},
            {"path": "k8s/m_ingress.yaml", "ext": ".yaml"},
        ]
    }
    result = detect(file_index)

    evidence = result["evidence_files"]
    assert evidence == sorted(evidence)


def test_deployment_infrastructure_docker_directory():
    """Test detection of files in docker/ directory."""
    file_index = {
        "files": [
            {"path": "docker/app.Dockerfile", "ext": ".Dockerfile"},
            {"path": "docker/nginx.Dockerfile", "ext": ".Dockerfile"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "docker" in result["found_patterns"]


def test_deployment_infrastructure_dockerignore():
    """Test detection of .dockerignore file."""
    file_index = {
        "files": [
            {"path": ".dockerignore", "ext": ""},
            {"path": "Dockerfile", "ext": ""},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert ".dockerignore" in result["evidence_files"]


def test_deployment_infrastructure_k8s_patterns():
    """Test various Kubernetes file patterns."""
    file_index = {
        "files": [
            {"path": "k8s/deployment.yaml", "ext": ".yaml"},
            {"path": "kubernetes/service.yaml", "ext": ".yaml"},
            {"path": "manifests/deployment.yaml", "ext": ".yaml"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "kubernetes" in result["found_patterns"]


def test_deployment_infrastructure_empty_file_index():
    """Test handling of empty file index."""
    file_index = {}
    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert result["evidence_files"] == []
    assert result["meta"]["docker_configs"] == 0


def test_deployment_infrastructure_case_sensitivity():
    """Test case-insensitive pattern matching."""
    file_index = {
        "files": [
            {"path": "K8S/Deployment.yaml", "ext": ".yaml"},
            {"path": "KUBERNETES/Service.yaml", "ext": ".yaml"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    # Should detect kubernetes (case-insensitive)
    assert "kubernetes" in result["found_patterns"]


def test_deployment_infrastructure_terraform_directory():
    """Test detection of terraform directory."""
    file_index = {
        "files": [
            {"path": "terraform/main.tf", "ext": ".tf"},
            {"path": "terraform/outputs.tf", "ext": ".tf"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "deployment-infrastructure"
    assert "terraform" in result["found_patterns"]


def test_deployment_infrastructure_mixed_deployment():
    """Test detection of mixed deployment approaches."""
    file_index = {
        "files": [
            {"path": "Dockerfile", "ext": ""},
            {"path": "k8s/deployment.yaml", "ext": ".yaml"},
            {"path": "terraform/eks.tf", "ext": ".tf"},
        ]
    }
    result = detect(file_index)

    assert len(result["found_patterns"]) >= 3
    assert "docker" in result["found_patterns"]
    assert "kubernetes" in result["found_patterns"]
    assert "terraform" in result["found_patterns"]
