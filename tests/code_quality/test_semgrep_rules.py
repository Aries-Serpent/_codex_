import shutil
import subprocess

import pytest

SEMGREP = shutil.which("semgrep")


@pytest.mark.skipif(SEMGREP is None, reason="semgrep not installed")
def test_semgrep_no_violations() -> None:
    result = subprocess.run(
        ["semgrep", "--config", "semgrep_rules/", "src"],
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout.decode()
