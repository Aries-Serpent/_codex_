from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: list[str]) -> list[str]:
    env = {**os.environ, "PYTHONPATH": "src"}
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env, cwd=ROOT)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def test_sweep_expand(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.yaml"
    sweep.write_text("a: [1,2]\nb: [3]\n")
    out = _run(["python", "scripts/run_sweep.py", "--sweep-file", str(sweep), "--dry-run"])
    assert any("{'a': 1, 'b': 3}" in line for line in out)
    assert len(out) == 2
    out2 = _run(
        [
            "python",
            "scripts/run_sweep.py",
            "--sweep-file",
            str(sweep),
            "--dry-run",
            "--max-runs",
            "1",
        ]
    )
    assert len(out2) == 1
