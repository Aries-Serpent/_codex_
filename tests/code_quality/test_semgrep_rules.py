"""
Test Semgrep Rules

Test module for semgrep rules.
"""

import os
import shutil
import subprocess

import pytest

SEMGREP = shutil.which("semgrep")


@pytest.mark.skipif(SEMGREP is None, reason="semgrep not installed")
def test_semgrep_no_violations() -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env.setdefault("SEMGREP_COLOR", "never")
    env.setdefault("SEMGREP_DISABLE_LIVE_PROGRESS", "1")

    result = subprocess.run(
        ["semgrep", "--config", "semgrep_rules/", "src"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    output = f"{result.stdout}\n{result.stderr}" if result.stdout or result.stderr else ""
    assert result.returncode == 0, output
