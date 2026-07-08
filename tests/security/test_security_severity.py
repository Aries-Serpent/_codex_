"""
Test: Security Severity Classification (P5)
- Builds a synthetic secret_entropy_report.json with varied entropy/length
- Ensures classification counts and weighting structure
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")


def setup_entropy():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()
    findings = [
        {"file": "f1.txt", "span": "AKIAABCDEFGHIJKLMNOP", "entropy": 4.20},
        {"file": "f2.txt", "span": "123e4567-e89b-12d3-a456-426614174000", "entropy": 3.90},
        {"file": "f3.txt", "span": "moderateEntropyTokenXYZ", "entropy": 3.60},
        {"file": "f4.txt", "span": "lowentropy", "entropy": 2.10},
    ]
    (ART / "secret_entropy_report.json").write_text(
        json.dumps({"findings": findings}, indent=2), encoding="utf-8"
    )


def test_severity_classification():
    setup_entropy()
    env = os.environ.copy()
    env["SECURITY_SEVERITY_ENABLE"] = "1"
    subprocess.run([sys.executable, "scripts/security/classify_severity.py"], check=True, env=env)
    out = ART / "security_severity.json"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())
    assert data["counts"]["high"] == 1, "Data must not be empty"
    assert data["counts"]["medium"] == 1, "Data must not be empty"
    assert data["counts"]["low"] == 1, "Data must not be empty"
    assert data["counts"]["total"] == 3, "Data must not be empty"
    assert "weights" in data, "Data must not be empty"
