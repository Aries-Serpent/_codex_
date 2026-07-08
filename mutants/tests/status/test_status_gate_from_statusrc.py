"""
Test Status Gate From Statusrc

Test module for status gate from statusrc.
"""

import json
import subprocess
import sys


def test_status_gate_with_coverage(tmp_path, monkeypatch):
    # Write .statusrc.json
    (tmp_path / ".statusrc.json").write_text(
        json.dumps({"fail_under_coverage": 35}), encoding="utf-8"
    )
    # Write minimal coverage
    coverage = {"totals": {"percent_covered": 40.0}}
    (tmp_path / ".coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
    code = subprocess.call(
        [sys.executable, "-c", "import tools.status_gate_from_statusrc as s; s.main()"],
        cwd=str(tmp_path),
    )
    assert code == 0, "code is not valid"


def test_status_gate_fail_when_below_threshold(tmp_path, monkeypatch):
    (tmp_path / ".statusrc.json").write_text(
        json.dumps({"fail_under_coverage": 50}), encoding="utf-8"
    )
    coverage = {"totals": {"percent_covered": 40.0}}
    (tmp_path / ".coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
    code = subprocess.call(
        [sys.executable, "-c", "import tools.status_gate_from_statusrc as s; s.main()"],
        cwd=str(tmp_path),
    )
    assert code == 1, "code is not valid"
