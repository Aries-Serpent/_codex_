import shutil
import subprocess

import pytest

BLACK = shutil.which("black")


@pytest.mark.skipif(BLACK is None, reason="black not installed")
def test_black_check_passes() -> None:
    result = subprocess.run(["black", "--check", "src", "tests"], capture_output=True)
    assert result.returncode == 0, result.stdout.decode()
