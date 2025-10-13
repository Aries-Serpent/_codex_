from __future__ import annotations

import json
from pathlib import Path

from codex.knowledge.build import build_kb


def test_build_kb(tmp_path: Path):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "guide.md").write_text("# Title\nHello\n\n## Use\nDo X\n", encoding="utf-8")
    out = tmp_path / "artifacts" / "kb.ndjsonl"
    build_kb(d, out)
    assert out.exists()
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    rec = json.loads(lines[0])
    assert "id" in rec and "text" in rec and "meta" in rec
