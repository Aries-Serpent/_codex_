from __future__ import annotations

import json

import pytest

typer = pytest.importorskip("typer", reason="typer not installed")
click = pytest.importorskip("click", reason="click not installed")
if not hasattr(typer, "Typer"):
    pytest.skip("typer missing Typer attribute", allow_module_level=True)
from typer.testing import CliRunner  # type: ignore  # noqa: E402

from codex_ml.cli import manifest as cli  # noqa: E402


def test_init_writes_valid_manifest(tmp_path):
    out = tmp_path / "m.json"
    runner = CliRunner()
    res = runner.invoke(cli.app, ["init", "--out", str(out), "--run-id", "r1"])
    assert res.exit_code == 0 and out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "codex.checkpoint.v2"
    assert data["run"]["id"] == "r1"
