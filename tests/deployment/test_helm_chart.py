import shutil
import subprocess

import pytest

HELM = shutil.which("helm")


@pytest.mark.skipif(HELM is None, reason="helm executable not available")
def test_helm_lint_passes() -> None:
    result = subprocess.run(["helm", "lint", "deploy/helm"], capture_output=True)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.skipif(HELM is None, reason="helm executable not available")
def test_helm_template_renders() -> None:
    result = subprocess.run(
        ["helm", "template", "test-release", "deploy/helm"], capture_output=True
    )
    assert result.returncode == 0
    assert b"Deployment" in result.stdout
