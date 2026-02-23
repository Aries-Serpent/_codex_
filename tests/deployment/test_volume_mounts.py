"""
Test Volume Mounts

Test module for volume mounts.
"""

from pathlib import Path


def test_compose_defines_required_volumes() -> None:
    """Verify docker-compose.yml defines required volume mounts for data and artifacts."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    # Volume mounts should map local directories to container paths
    # Actual mounts are ./data:/app/data and ./artifacts:/app/artifacts (not root paths)
    assert "./data:/app/data" in compose, "Missing data volume mount"
    assert "./artifacts:/app/artifacts" in compose, "Missing artifacts volume mount"
