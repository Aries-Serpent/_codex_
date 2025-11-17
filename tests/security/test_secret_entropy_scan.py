"""
Entropy Scan Test (P4)
- Creates artificial high-entropy string
- Confirms detection
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")


def setup():
    if ART.exists():
        shutil.rmtree(ART)
    Path("secrets.txt").write_text(
        "NORMALDATA\nAKIAABCDEFGHIJKLMNOP\nRANDOMHIGHENTROPYabcXYZ1234567890", encoding="utf-8"
    )


def test_entropy_scan():
    setup()
    env = os.environ.copy()
    env["SECRET_ENTROPY_THRESHOLD"] = "3.0"
    subprocess.run([sys.executable, "scripts/security/secret_entropy_scan.py"], check=True, env=env)
    rep = ART / "secret_entropy_report.json"
    assert rep.exists()
    data = json.loads(rep.read_text())
    assert data["count"] > 0
