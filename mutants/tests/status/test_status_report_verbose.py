"""
Test Status Report Verbose

Test module for status report verbose.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_status_report_verbose_and_artifacts(tmp_path):
    output_path = tmp_path / "STATUS_REPORT.md"
    proc = subprocess.run(
        [
            sys.executable,
            "tools/status_report.py",
            "--summary",
            "samples/assistant_message_summary.sample.json",
            "--selected",
            "2",
            "--verbose",
            "--save-logs",
            "--out",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert proc.returncode in (0, 1)
    report_text = output_path.read_text(encoding="utf-8")
    assert "Artifacts:" in report_text, "Condition must be true"
    assert (REPO_ROOT / ".codex/status").exists(), "Condition must be true"
