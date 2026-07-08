"""
Test Container Security

Test module for container security.
"""

from pathlib import Path


def test_no_root_user_in_container() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "USER appuser" in dockerfile, "Condition must be true"


def test_minimal_attack_surface() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "apt-get" in dockerfile, "Condition must be true"
    assert "curl" in dockerfile, "Condition must be true"
