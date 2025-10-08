from __future__ import annotations

import json
import re

import pytest

typer = pytest.importorskip("typer", reason="typer not installed")
click = pytest.importorskip("click", reason="click not installed")
if not hasattr(typer, "Typer"):
    pytest.skip("typer missing Typer attribute", allow_module_level=True)
from typer.testing import CliRunner  # type: ignore  # noqa: E402

from codex_ml.cli import manifest as manifest_cli  # noqa: E402
from codex_ml.checkpointing import schema_v2  # noqa: E402


def test_hash_and_readme_update(tmp_path):
    mpath = tmp_path / "manifest.json"
    readme = tmp_path / "README.md"
    manifest = {
        "schema": "codex.checkpoint.v2",
        "run": {"id": "abc", "created_at": "2025-10-07T00:00:00Z"},
        "weights": {"format": "pt", "bytes": 10},
    }
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    readme.write_text("# Title\n\n", encoding="utf-8")
    expected = schema_v2.digest(manifest)
    runner = CliRunner()
    res = runner.invoke(
        manifest_cli.app,
        ["hash", "--path", str(mpath), "--update-readme", str(readme)],
    )
    assert res.exit_code == 0
    out = res.stdout.strip().splitlines()[-1]
    assert re.fullmatch(r"[0-9a-f]{64}", out) and out == expected
    txt = readme.read_text(encoding="utf-8")
    assert "<!-- manifest-digest:start -->" in txt and expected[:12] in txt
