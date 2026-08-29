"""
Test Selection Report Smoke

Test module for selection report smoke.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    not Path("samples/assistant_message_summary.sample.json").exists(),
    reason="sample summary not present; skip selection smoke test",
)
def test_selection_report_smoke(tmp_path: Path) -> None:
    out = tmp_path / "SELECTION_REPORT.md"
    repo_root = Path(__file__).resolve().parents[2]
    rc = subprocess.run(
        [
            sys.executable,
            "tools/selection_report.py",
            "--summary",
            "samples/assistant_message_summary.sample.json",
            "--out",
            str(out),
        ],
        check=False,
        cwd=str(repo_root),
    ).returncode
    assert rc in (0, 1, 2), "selection_report should exit with realistic, non-crashing code"
    assert out.exists(), "SELECTION_REPORT.md not created"
    text = out.read_text(encoding="utf-8")
    assert "Selection Report — *codex*" in text, "Condition must be true"
    assert "Recommendation" in text, "Condition must be true"
