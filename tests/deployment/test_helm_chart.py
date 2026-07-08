"""
Test Helm Chart

Test module for helm chart.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

HELM = shutil.which("helm")
HELM_CHART_DIR = Path("deploy/helm")
HAS_TEMPLATES = (HELM_CHART_DIR / "templates").exists()


@pytest.mark.skipif(HELM is None, reason="helm executable not available")
def test_helm_lint_passes() -> None:
    result = subprocess.run(["helm", "lint", "deploy/helm"], capture_output=True)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.skipif(HELM is None, reason="helm executable not available")
@pytest.mark.skipif(not HAS_TEMPLATES, reason="helm chart has no templates directory")
def test_helm_template_renders() -> None:
    result = subprocess.run(
        ["helm", "template", "test-release", "deploy/helm"], capture_output=True
    )
    assert result.returncode == 0, "Result must not be empty"
    assert b"Deployment" in result.stdout, "Result must not be empty"
