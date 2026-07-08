"""
Test Docker Build

Test module for docker build.
"""

import os
import shutil
import subprocess

import pytest

DOCKER = shutil.which("docker")
# Skip Docker build tests in CI due to pip install failures inside container
_SKIP_DOCKER_BUILD = (DOCKER is None) or os.environ.get("CI", "") == "true"


@pytest.mark.slow
@pytest.mark.skipif(_SKIP_DOCKER_BUILD, reason="Docker build not supported in CI")
def test_cpu_dockerfile_builds() -> None:
    cmd = ["docker", "build", "--target", "cpu-runtime", "-t", "codex:test-cpu", "."]
    result = subprocess.run(cmd, capture_output=True, timeout=1800)  # 30 min timeout
    assert result.returncode == 0, "Result must not be empty"


@pytest.mark.slow
@pytest.mark.skipif(_SKIP_DOCKER_BUILD, reason="Docker build not supported in CI")
def test_gpu_dockerfile_builds() -> None:
    cmd = ["docker", "build", "--target", "gpu-runtime", "-t", "codex:test-gpu", "."]
    result = subprocess.run(cmd, capture_output=True, timeout=1800)  # 30 min timeout
    assert result.returncode == 0, "Result must not be empty"
