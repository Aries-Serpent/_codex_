from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest


def test_hydra_train_prints_cfg(monkeypatch, tmp_path):
    # Import if available; allow stub environments to exercise the CLI error path.
    try:
        pytest.importorskip("hydra")
    except pytest.skip.Exception:
        pytest.skip("hydra not importable")
    monkeypatch.chdir(tmp_path)
    env = os.environ.copy()
    env["CODEX_SHOW_CFG"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "codex_ml", "hydra-train"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    output = proc.stdout.strip()
    if output.startswith("{"):
        payload = json.loads(output)
        assert payload.get("ok") is False
        assert "hydra-core" in payload.get("reason", "")
    else:
        assert "train:" in output or "epochs:" in output
