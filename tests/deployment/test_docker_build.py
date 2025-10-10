"""Lightweight checks that guard against Docker regressions without building images."""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = PROJECT_ROOT / "Dockerfile"


@pytest.mark.skipif(not DOCKERFILE.exists(), reason="Dockerfile missing")
def test_dockerfile_uses_multistage_build() -> None:
    contents = DOCKERFILE.read_text(encoding="utf-8")
    stages = [line for line in contents.splitlines() if line.startswith("FROM ")]
    assert len(stages) >= 2, "expected a multi-stage Dockerfile with at least two FROM statements"


@pytest.mark.skipif(not DOCKERFILE.exists(), reason="Dockerfile missing")
def test_dockerfile_non_root_user_defined() -> None:
    contents = DOCKERFILE.read_text(encoding="utf-8")
    assert "USER appuser" in contents, "runtime stage should drop privileges"
