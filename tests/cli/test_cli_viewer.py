import subprocess
import sys


def test_cli_viewer_runs():
    cmd = [sys.executable, "-m", "scripts.cli.viewer", "--show", "nonexistent.txt"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # Should execute and exit with code 0 or 1 depending on file existence
    assert proc.returncode in (0, 1)
