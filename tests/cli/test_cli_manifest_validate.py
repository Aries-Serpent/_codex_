from __future__ import annotations

import json

import pytest

typer = pytest.importorskip("typer", reason="typer not installed")
click = pytest.importorskip("click", reason="click not installed")
if not hasattr(typer, "Typer"):
    pytest.skip("typer missing Typer attribute", allow_module_level=True)
from typer.testing import CliRunner  # type: ignore  # noqa: E402

from codex_ml.cli import manifest as cli  # noqa: E402


def test_validate_ok_and_strict(tmp_path):
    manifest = {
        "schema": "codex.checkpoint.v2",
        "run": {"id": "x", "created_at": "2025-10-07T00:00:00Z"},
        "weights": {"format": "pt", "bytes": 1},
    }
    path = tmp_path / "m.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    runner = CliRunner()
    res = runner.invoke(cli.app, ["validate", "--path", str(path)])
    assert res.exit_code == 0

    manifest["foo"] = 1
    path.write_text(json.dumps(manifest), encoding="utf-8")
    res2 = runner.invoke(cli.app, ["validate", "--path", str(path), "--strict"])
    assert res2.exit_code == 2
