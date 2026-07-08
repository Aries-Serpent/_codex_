"""
Test Report Merge

Test module for report merge.
"""

import json
import subprocess
import sys


def test_report_merge(tmp_path):
    report = tmp_path / "r.json"
    report.write_text(
        json.dumps(
            {
                "metadata": {
                    "title": "t",
                    "timestamp_utc": "x",
                    "report_version": "v1",
                    "template_version": "v1.2",
                },
                "snapshot": {},
                "delta": {},
                "patches": [],
                "automation": {},
                "security": {},
                "questions": [],
                "decisions": [],
            }
        ),
        encoding="utf-8",
    )
    frag = tmp_path / "m.json"
    frag.write_text(json.dumps({"a": 1}), encoding="utf-8")
    code = subprocess.call(
        [
            sys.executable,
            "tools/report_merge.py",
            "--report",
            str(report),
            "--in",
            f"{frag}:automation.performance",
        ]
    )
    assert code == 0, "code is not valid"
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["automation"]["performance"] == {"a": 1}, "Data must not be empty"
