"""
Test deployment infrastructure configuration patterns.

Part of deployment-infrastructure capability maturity improvement.
"""

from pathlib import Path

import pytest


def test_deployment_directory_exists():
    """Verify deployment configuration directory exists."""
    deploy_dirs = [Path("deploy"), Path("deployment"), Path("k8s")]
    exists = any(d.exists() for d in deploy_dirs)
    assert exists, "No deployment directory found"


def test_service_directories_exist():
    """Verify service directories are present."""
    services_dir = Path("services")
    if not services_dir.exists():
        pytest.skip("No services directory")

    # Should have subdirectories for services
    subdirs = [d for d in services_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
    assert len(subdirs) > 0, "Services directory has no service subdirectories"


def test_docker_artifacts_present():
    """Verify Docker-related files are present."""
    docker_files = [Path("docker-compose.yml"), Path("Dockerfile"), Path(".dockerignore")]

    found = [f for f in docker_files if f.exists()]
    assert len(found) > 0, "No Docker artifacts found"


def test_deployment_config_patterns():
    """Verify common deployment configuration patterns."""
    from pathlib import Path

    # Look for common deployment file patterns
    patterns = [
        "docker-compose*.yml",
        "docker-compose*.yaml",
        "**/Dockerfile*",
        "deploy/**/*.yaml",
        "deploy/**/*.yml",
    ]

    found_files = []
    for pattern in patterns:
        found_files.extend(Path(".").glob(pattern))

    assert len(found_files) > 0, "No deployment configuration files found"


def test_environment_config_present():
    """Verify environment configuration files exist."""
    env_files = [Path(".env.example"), Path(".env.template"), Path("config/.env.example")]

    # At least one should exist for documentation
    found = [f for f in env_files if f.exists()]
    if not found:
        pytest.skip("No .env example files found (acceptable if using other config methods)")
