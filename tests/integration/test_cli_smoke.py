import os
import subprocess
import sys
from pathlib import Path

import pytest

import hydra

pytest.importorskip("omegaconf")

if hasattr(hydra, "_CONFIG_STACK"):
    pytest.skip("Hydra extra stub active; CLI requires hydra-core", allow_module_level=True)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {
    **os.environ,
    "CODEX_ALLOW_MISSING_HYDRA_EXTRA": os.environ.get("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1"),
}


def test_cli_runs_and_prints_config():
    proc = subprocess.run(
        [sys.executable, "-m", "hhg_logistics.main"],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(PROJECT_ROOT),
        env=ENV,
    )
    assert "Composed config:" in proc.stdout
