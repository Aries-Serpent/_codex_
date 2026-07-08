"""
Test Cli Manifest Init

Test module for cli manifest init.
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip("typer")


typer = pytest.importorskip("typer", reason="typer not installed")
click = pytest.importorskip("click", reason="click not installed")
if not hasattr(typer, "Typer"):
    pytest.skip("typer missing Typer attribute", allow_module_level=True)
from typer.testing import CliRunner  # type: ignore

from codex_ml.cli import manifest as cli


def test_init_writes_valid_manifest(tmp_path):
    out = tmp_path / "m.json"
    runner = CliRunner()
    res = runner.invoke(cli.app, ["init", "--out", str(out), "--run-id", "r1"])
    assert res.exit_code == 0 and out.exists(), "exit_code is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "codex.checkpoint.v2", "Data must not be empty"
    assert data["run"]["id"] == "r1", "Data must not be empty"
