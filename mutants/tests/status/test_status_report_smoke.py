"""
Test Status Report Smoke

Test module for status report smoke.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    not Path("samples/assistant_message_summary.sample.json").exists(),
    reason="sample summary not present; skip smoke run",
)
def test_status_report_template_mode(tmp_path: Path) -> None:
    out = tmp_path / "STATUS_REPORT.md"
    repo_root = Path(__file__).resolve().parents[2]
    cmd = [
        sys.executable,
        "tools/status_report.py",
        "--summary",
        "samples/assistant_message_summary.sample.json",
        "--selected",
        "3",
        "--template",
        "docs/templates/status_update.md",
        "--branch",
        "test/branch",
        "--pr",
        "1234",
        "--out",
        str(out),
    ]
    rc = subprocess.run(cmd, check=False, cwd=repo_root).returncode
    assert rc in (0, 1), "status_report should exit 0 (all pass) or 1 (some gate failed)"
    assert out.exists(), "STATUS_REPORT.md was not created"
    text = out.read_text(encoding="utf-8")
    # Basic template sections should be present
    assert "Gates Summary" in text, "Condition must be true"
    assert "Repo Map" in text, "Condition must be true"
    assert "Capability Audit Table" in text, "Condition must be true"
