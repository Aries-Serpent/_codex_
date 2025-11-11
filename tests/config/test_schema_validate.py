"""
Test: schema_validate.py (P4)
- Ensures report generated even if workflow.yaml present
- Validates normalized weights warning absent when sum==1
"""
import json
import subprocess
import sys
from pathlib import Path


def test_schema_validation():
    subprocess.run([sys.executable,"scripts/config/schema_validate.py"],check=True)
    rep = Path("audit_artifacts/schema_validation_report.json")
    assert rep.exists()
    data = json.loads(rep.read_text())
    assert "workflow_warnings" in data
    assert not any(w == "weights_not_normalized" for w in data.get("workflow_warnings",[]))
