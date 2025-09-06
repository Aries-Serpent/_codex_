import subprocess
import sys
from pathlib import Path


def test_verify_pins(tmp_path: Path) -> None:
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text("[project]\ndependencies=['foo']\n")
    res = subprocess.run(
        [sys.executable, "tools/verify_pins.py", str(pyproj)],
        capture_output=True,
    )
    assert res.returncode != 0
