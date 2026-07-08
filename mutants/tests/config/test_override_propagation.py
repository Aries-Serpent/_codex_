"""
Test Override Propagation

Test module for override propagation.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

# Skip these tests if hydra is not available in the environment
pytest.importorskip("hydra")

# Skip when the Typer CLI is active: --override-file is only supported in the
# Hydra-backed CLI path.  When typer is installed, codex_ml.cli.main uses the
# Typer app which does not accept this flag.
try:
    import codex_ml.cli.main as _cli_main

    if hasattr(_cli_main, "_typer_cli_wrapper"):
        pytest.skip(
            "--override-file requires the Hydra CLI path; typer CLI is active",
            allow_module_level=True,
        )
except ImportError:
    pytest.skip("codex_ml.cli.main not available", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[2]


def test_override_file(tmp_path: Path) -> None:
    override_file = tmp_path / "ovr.txt"
    override_file.write_text("train.batch_size=2\ntrain.lr=0.1\n")
    cmd = [
        "python",
        "-m",
        "codex_ml.cli.main",
        f"--override-file={override_file}",
        "--set",
        "tokenizer.name=gpt2",
        "pipeline.steps=[]",
        "dry_run=true",
        "hydra.run.dir=.codex/hydra_last",
    ]
    env = {**os.environ, "PYTHONPATH": "src"}
    subprocess.run(cmd, check=True, env=env, cwd=ROOT)
    text = (ROOT / ".codex/hydra_last/.hydra/config.yaml").read_text()
    assert "batch_size: 2" in text, "Condition must be true"
    assert "lr: 0.1" in text, "Condition must be true"
    assert "name: gpt2" in text, "Condition must be true"
