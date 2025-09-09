import subprocess
import sys
import os
from pathlib import Path

import pytest

pytest.importorskip("hydra")


def test_hydra_cli_smoke():
    cmd = [sys.executable, "-m", "codex_ml.cli.main", "dry_run=true", "pipeline.steps=[]"]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    subprocess.run(cmd, check=True, env=env)


def test_hydra_cli_help():
    cmd = [sys.executable, "-m", "codex_ml.cli.main", "--help"]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    assert "Hydra" in proc.stdout
