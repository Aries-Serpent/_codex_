import shutil
import subprocess

import pytest

RUFF = shutil.which("ruff")


@pytest.mark.skipif(RUFF is None, reason="ruff not installed")
def test_ruff_passes() -> None:
    result = subprocess.run(["ruff", "check", "src", "tests"], capture_output=True)
    assert result.returncode == 0, result.stdout.decode()
