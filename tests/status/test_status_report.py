"""
Test Status Report

Test module for status report.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    try:
        return subprocess.run(cmd, check=False).returncode
    except Exception as _err:
        return 127


def test_status_report_creates_markdown(tmp_path: Path, monkeypatch):
    # Work from repo root; output to tmp file
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.chdir(repo_root)
    out = tmp_path / "STATUS_REPORT.md"
    rc = run(
        [
            sys.executable,
            "tools/status_report.py",
            "--summary",
            "samples/assistant_message_summary.sample.json",
            "--selected",
            "3",
            "--out",
            str(out),
        ]
    )
    assert rc in (0, 1), "status_report should exit 0 (all pass) or 1 (some gate failed)"
    assert out.exists(), "STATUS_REPORT.md was not created"
    t = out.read_text(encoding="utf-8")
    assert t, "STATUS_REPORT.md content must not be empty"
    for section in ("Gates Summary", "Highlights", "Next Steps"):
        assert section in t, "Condition must be true"
