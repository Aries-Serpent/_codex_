"""
Test docker-compose.yml configuration validity and service definitions.

Part of deployment-infrastructure capability maturity improvement.
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def docker_compose_file():
    """Return path to docker-compose.yml file."""
    return Path("docker-compose.yml")


def test_docker_compose_exists(docker_compose_file):
    """Verify docker-compose.yml file exists."""
    assert docker_compose_file.exists(), "docker-compose.yml not found"


def test_docker_compose_valid_yaml(docker_compose_file):
    """Verify docker-compose.yml is valid YAML."""
    with open(docker_compose_file) as f:
        config = yaml.safe_load(f)
    assert config is not None, "config must be initialized"
    assert "services" in config or "version" in config, "Condition must be true"


def test_docker_compose_service_definitions(docker_compose_file):
    """Verify all services have required fields."""
    with open(docker_compose_file) as f:
        config = yaml.safe_load(f)

    services = config.get("services", {})
    if not services:
        pytest.skip("No services defined in docker-compose.yml")

    for service_name, service_config in services.items():
        # Each service should have image or build
        has_image_or_build = "image" in service_config or "build" in service_config
        assert has_image_or_build, f"Service {service_name} missing image/build"


def test_docker_compose_network_config(docker_compose_file):
    """Verify network configuration if present."""
    with open(docker_compose_file) as f:
        config = yaml.safe_load(f)

    # Check if networks are defined (optional)
    if "networks" in config:
        assert isinstance(config["networks"], dict)


def test_docker_compose_volume_mounts(docker_compose_file):
    """Verify volume mounts are properly configured."""
    with open(docker_compose_file) as f:
        config = yaml.safe_load(f)

    services = config.get("services", {})
    for service_name, service_config in services.items():
        if "volumes" in service_config:
            volumes = service_config["volumes"]
            assert isinstance(volumes, list), f"Service {service_name} volumes must be a list"
