#!/usr/bin/env python3
"""CLI smoke tests for the evaluation runner (Typer app)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("datasets")

from typer.testing import CliRunner  # noqa: E402

from codex_ml.eval import eval_runner  # noqa: E402


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
    assert result.exit_code == 0
    nd = out_dir / "metrics.ndjson"
    csv = out_dir / "metrics.csv"
    assert nd.exists()
    assert csv.exists()
    rec = json.loads(nd.read_text().strip().splitlines()[0])
    assert rec["dataset"] == "toy_copy_task"
    assert rec["metric"] == "exact_match"
