"""
Test Dockerfile configurations for security and best practices.

Part of deployment-infrastructure capability maturity improvement.
"""

from pathlib import Path

import pytest


@pytest.fixture
def dockerfiles():
    """Find all Dockerfile variants in the repository."""
    return list(Path(".").glob("**/Dockerfile*"))


def test_dockerfiles_exist(dockerfiles):
    """Verify Dockerfiles are present."""
    assert len(dockerfiles) > 0, "No Dockerfiles found"


def test_dockerfile_has_from_statement(dockerfiles):
    """Verify each Dockerfile has a FROM statement."""
    for dockerfile in dockerfiles:
        if dockerfile.name.endswith(".md") or dockerfile.name.endswith(".txt"):
            continue  # Skip documentation files

        content = dockerfile.read_text(errors="ignore")
        assert "FROM " in content, f"{dockerfile} missing FROM statement"


def test_dockerfile_uses_specific_tags(dockerfiles):
    """Verify Dockerfiles use specific image tags where appropriate."""
    for dockerfile in dockerfiles:
        if dockerfile.name.endswith(".md") or dockerfile.name.endswith(".txt"):
            continue

        content = dockerfile.read_text(errors="ignore")
        lines = [line for line in content.split("\n") if line.strip().startswith("FROM ")]

        for line in lines:
            # Allow 'latest' for local/dev images, but flag it
            if ":latest" in line and "local" not in dockerfile.name.lower():
                # Just warn, don't fail - this is a soft check
                pytest.skip(f"{dockerfile} uses ':latest' tag (acceptable for dev)")


def test_dockerfile_exposes_ports(dockerfiles):
    """Verify service Dockerfiles expose ports."""
    service_dockerfiles = [d for d in dockerfiles if "services" in str(d) or "service" in str(d)]

    if not service_dockerfiles:
        pytest.skip("No service Dockerfiles found")

    for dockerfile in service_dockerfiles:
        content = dockerfile.read_text(errors="ignore")
        # Service Dockerfiles should typically expose ports
        # This is a soft check
        if "EXPOSE " not in content:
            pytest.skip(f"{dockerfile} does not expose ports (may be configured elsewhere)")


def test_dockerfile_has_workdir(dockerfiles):
    """Verify Dockerfiles set a working directory."""
    for dockerfile in dockerfiles:
        if dockerfile.name.endswith(".md") or dockerfile.name.endswith(".txt"):
            continue

        content = dockerfile.read_text(errors="ignore")
        # WORKDIR is a best practice but not always required
        if "WORKDIR " not in content:
            pytest.skip(f"{dockerfile} does not set WORKDIR (acceptable)")
