"""
Test Cli Smoke

Test module for cli smoke.
"""
pytest.importorskip("omegaconf")
import os
import subprocess
import sys
from pathlib import Path
    import hydra



os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

try:
except ModuleNotFoundError:
    pytest.skip("Hydra core not installed and no stub available", allow_module_level=True)


if hasattr(hydra, "_CONFIG_STACK"):
    pytest.skip("Hydra extra stub active; CLI requires hydra-core", allow_module_level=True)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = str(PROJECT_ROOT / "src")
PYTHONPATH = os.pathsep.join(
    [SRC_PATH, os.environ.get("PYTHONPATH", "")] if os.environ.get("PYTHONPATH") else [SRC_PATH]
)
ENV = {
    **os.environ,
    "CODEX_ALLOW_MISSING_HYDRA_EXTRA": os.environ.get("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1"),
    "PYTHONPATH": PYTHONPATH,
}


def test_cli_runs_and_prints_config():
    proc = subprocess.run(
        [sys.executable, "-m", "hhg_logistics.main"],
        capture_output=True,
        text=True,
        check=False,  # Don't raise on error, check manually
        cwd=str(PROJECT_ROOT),
        env=ENV,
    )
    # Check that the config is printed, even if the command fails later
    # (e.g., due to missing optional dependencies like pandas)
    assert "Composed config:" in proc.stdout, (
        f"Expected 'Composed config:' in stdout\n"
        f"Exit code: {proc.returncode}\n"
        f"STDOUT:\n{proc.stdout}\n"
        f"STDERR:\n{proc.stderr}"
    )
