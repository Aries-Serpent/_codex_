import shutil
import subprocess

import pytest

ISORT = shutil.which("isort")


@pytest.mark.skipif(ISORT is None, reason="isort not installed")
def test_isort_compliance() -> None:
    result = subprocess.run(["isort", "--check-only", "src", "tests"], capture_output=True)
    assert result.returncode == 0, result.stdout.decode()
