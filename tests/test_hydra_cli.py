import subprocess
import sys

import pytest

pytest.importorskip("hydra")


def test_hydra_cli_smoke():
    cmd = [sys.executable, "-m", "src.codex_ml.cli.main", "dry_run=true", "pipeline.steps=[]"]
    subprocess.run(cmd, check=True)
