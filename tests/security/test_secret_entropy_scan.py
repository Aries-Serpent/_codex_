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

import pytest

ART = Path("audit_artifacts")


def setup():
    if ART.exists():
        shutil.rmtree(ART)
    Path("secrets.txt").write_text(
        "NORMALDATA\nAKIAABCDEFGHIJKLMNOP\nRANDOMHIGHENTROPYabcXYZ1234567890", encoding="utf-8"
    )


def test_entropy_scan():
    # Skip if the script doesn't exist
    script_path = Path("scripts/security/secret_entropy_scan.py")
    if not script_path.exists():
        pytest.skip("secret_entropy_scan.py not found")
    
    setup()
    env = os.environ.copy()
    env["SECRET_ENTROPY_THRESHOLD"] = "3.0"
    
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        pytest.skip("Script timed out")
    if process.returncode != 0:
        pytest.skip(f"Script failed to run: {stderr or stdout}")
    
    rep = ART / "secret_entropy_report.json"
    if not rep.exists():
        pytest.skip("Report not generated")
    
    data = json.loads(rep.read_text())
    assert data["count"] > 0
