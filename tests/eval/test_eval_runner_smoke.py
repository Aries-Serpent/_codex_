#!/usr/bin/env python3
"""Test Eval Runner Smoke

CLI smoke tests for the evaluation runner (Typer app).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("typer")


pytest.importorskip("datasets")

from typer.testing import CliRunner

from codex_ml.eval import eval_runner


def test_eval_runner_smoke(tmp_path: Path):
    runner = CliRunner()
    out_dir = tmp_path / "out"
    result = runner.invoke(
        eval_runner.app,
        [
            "--datasets",
            "toy_copy_task",
            "--metrics",
            "exact_match",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert result.exit_code == 0, "Result must not be empty"
    nd = out_dir / "metrics.ndjson"
    csv = out_dir / "metrics.csv"
    assert nd.exists(), "Condition must be true"
    assert csv.exists(), "Condition must be true"
    rec = json.loads(nd.read_text().strip().splitlines()[0])
    assert rec["dataset"] == "toy_copy_task", "Data must not be empty"
    assert rec["metric"] == "exact_match", "Condition must be true"
