import json
from pathlib import Path
import subprocess
import sys


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
    code = subprocess.call([sys.executable, "tools/sarif_aggregate.py", "--in", str(s1), str(s2), "--out", str(out)])
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0"
    assert len(data["runs"]) == 2
    assert data["runs"][0]["results"][0]["ruleId"] == "rule-a"
    assert data["runs"][1]["results"][0]["ruleId"] == "rule-b"
