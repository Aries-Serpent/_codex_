from __future__ import annotations

import json
from pathlib import Path

from codex.knowledge.build import build_kb


def test_build_kb_from_docs(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "crm"
    docs.mkdir(parents=True, exist_ok=True)
    guide = docs / "guide.md"
    guide.write_text(
        "# Intro\nThis is a test document.\n\n## Usage\nCall the CLI.\n",
        encoding="utf-8",
    )
    out = tmp_path / "artifacts" / "kb.ndjsonl"
    res = build_kb(tmp_path / "docs", out)
    assert out.exists()
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    assert res["written"] >= 1
    first = json.loads(lines[0])
    assert "id" in first and "text" in first and "meta" in first
    assert first["meta"]["lang"] == "en"
