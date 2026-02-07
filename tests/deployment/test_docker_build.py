"""
Test Docker Build

Test module for docker build.
"""

import shutil
import subprocess

import pytest

DOCKER = shutil.which("docker")


@pytest.mark.slow
@pytest.mark.skipif(DOCKER is None, reason="docker executable not available")
def test_cpu_dockerfile_builds() -> None:
    cmd = ["docker", "build", "--target", "cpu-runtime", "-t", "codex:test-cpu", "."]
    result = subprocess.run(cmd, capture_output=True, timeout=1800)  # 30 min timeout
    assert result.returncode == 0


@pytest.mark.slow
@pytest.mark.skipif(DOCKER is None, reason="docker executable not available")
def test_gpu_dockerfile_builds() -> None:
    cmd = ["docker", "build", "--target", "gpu-runtime", "-t", "codex:test-gpu", "."]
    result = subprocess.run(cmd, capture_output=True, timeout=1800)  # 30 min timeout
    assert result.returncode == 0
