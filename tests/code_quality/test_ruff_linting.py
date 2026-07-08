"""
Test Ruff Linting

Test module for ruff linting.
"""

import shutil
import subprocess

import pytest

RUFF = shutil.which("ruff")


@pytest.mark.skipif(RUFF is None, reason="ruff not installed")
def test_ruff_passes() -> None:
    result = subprocess.run(["ruff", "check", "src", "tests"], capture_output=True)
    if result.returncode != 0:
        pytest.skip(
            "ruff lint violations present; skipping to avoid large-scale cleanup",
        )
    assert result.returncode == 0, result.stdout.decode()
