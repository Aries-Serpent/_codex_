"""
Test Requirements Dev

Test module for requirements dev.
"""

from __future__ import annotations

from pathlib import Path


def test_requirements_dev_contains_core_tools() -> None:
    p = Path("requirements-dev.txt")
    assert p.exists(), "requirements-dev.txt missing"
    content = p.read_text(encoding="utf-8").lower()
    for need in ("pre-commit", "nox", "pytest", "jsonschema"):
        assert need in content, f"{need} not listed in requirements-dev.txt"
