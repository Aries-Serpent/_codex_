"""
Test Cli Smoke

Test module for cli smoke.
"""

import json
from pathlib import Path

from codex_digest.cli import main


def test_cli_smoke(tmp_path: Path):
    desc = tmp_path / "desc.md"
    desc.write_text("Plan tasks and build pipeline with coverage.", encoding="utf-8")
    md = tmp_path / ".out.md"
    js = tmp_path / ".out.json"
    rc = main(["--input-file", str(desc), "--out-md", str(md), "--out-json", str(js), "--dry-run"])
    assert rc == 0, "rc is not valid"
    assert md.exists() and js.exists(), "Condition must be true"
    plan = json.loads(js.read_text(encoding="utf-8"))
    assert "steps" in plan, "Condition must be true"
