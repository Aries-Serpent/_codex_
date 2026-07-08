"""
Test Tokenizer Cli Refresh

Test module for tokenizer cli refresh.
"""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.tokenization import cli


def test_refresh_creates_manifest(tmp_path: Path) -> None:
    model = tmp_path / "toy.model"
    model.write_text("", encoding="utf-8")
    cli.main(["refresh", str(model), "--notes", "demo"])
    manifest = json.loads(model.with_suffix(".provenance.json").read_text(encoding="utf-8"))
    assert manifest["model"].endswith("toy.model"), "Condition must be true"
    assert manifest["notes"] == "demo", "Condition must be true"
    assert manifest["timestamp"].endswith("Z"), "Condition must be true"
