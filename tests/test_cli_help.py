import os
import subprocess
import sys
from pathlib import Path


def test_cli_help_runs():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(["src", env.get("PYTHONPATH", "")])
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli.main", "--help"],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    assert result.returncode == 0
    assert "powered by hydra" in result.stdout.lower()
