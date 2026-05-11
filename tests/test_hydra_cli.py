"""
Test Codex ML CLI

Test module for codex_ml CLI (Typer-based).
"""

import os
import subprocess
import sys
from pathlib import Path


def test_cli_smoke():
    """Test that CLI can be invoked with --help."""
    cmd = [sys.executable, "-m", "codex_ml.cli.main", "--help"]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    assert result.returncode == 0


def test_cli_help():
    """Test that CLI help shows expected commands."""
    cmd = [sys.executable, "-m", "codex_ml.cli.main", "--help"]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    # Accept both Typer-style and Hydra fallback help outputs.
    assert (
        "Codex ML CLI" in proc.stdout
        or "Commands" in proc.stdout
        or "Hydra-managed pipeline entrypoint" in proc.stdout
    )
