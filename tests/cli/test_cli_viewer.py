import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_cli_viewer_runs():
    cmd = [sys.executable, "-m", "scripts.cli.viewer", "--show", "nonexistent.txt"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    # Should execute and exit with code 0 or 1 depending on file existence
    assert proc.returncode in (0, 1)


def test_cli_viewer_reads_readme():
    cmd = [sys.executable, "-m", "scripts.cli.viewer", "--show", "README.md"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    assert proc.returncode == 0
    assert "codex-universal" in proc.stdout
