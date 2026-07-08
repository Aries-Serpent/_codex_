"""
Test Sarif Aggregate

Test module for sarif aggregate.
"""

import json
import subprocess
import sys
from pathlib import Path


def write_sarif(p: Path, rule_id: str):
    sarif = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "semgrep", "version": "0.0.0"}},
                "results": [{"ruleId": rule_id, "message": {"text": "test finding"}}],
            }
        ],
    }
    p.write_text(json.dumps(sarif), encoding="utf-8")


def test_sarif_aggregate(tmp_path):
    s1 = tmp_path / "s1.sarif"
    s2 = tmp_path / "s2.sarif"
    out = tmp_path / "agg.sarif"
    write_sarif(s1, "rule-a")
    write_sarif(s2, "rule-b")
    code = subprocess.call(
        [
            sys.executable,
            "tools/sarif_aggregate.py",
            "--in",
            str(s1),
            str(s2),
            "--out",
            str(out),
        ]
    )
    assert code == 0, "code is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0", "Data must not be empty"
    assert len(data["runs"]) == 2, "Collection must not be empty"
    assert data["runs"][0]["results"][0]["ruleId"] == "rule-a", "Result must not be empty"
    assert data["runs"][1]["results"][0]["ruleId"] == "rule-b", "Result must not be empty"
