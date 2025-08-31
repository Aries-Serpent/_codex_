import subprocess
import sys

import pytest

pytest.importorskip("hydra")


def test_hydra_cli_smoke():
    cmd = [sys.executable, "-m", "src.codex_ml.cli.main", "dry_run=true", "pipeline.steps=[]"]
    subprocess.run(cmd, check=True)


def test_hydra_cli_help():
    cmd = [sys.executable, "-m", "src.codex_ml.cli.main", "--help"]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "Usage" in proc.stdout
