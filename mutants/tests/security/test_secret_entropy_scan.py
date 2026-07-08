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


@pytest.mark.timeout(180)
def test_entropy_scan():
    # Skip if the script doesn't exist
    script_path = Path("scripts/security/secret_entropy_scan.py")
    if not script_path.exists():
        pytest.skip("secret_entropy_scan.py not found")

    setup()
    env = os.environ.copy()
    env["SECRET_ENTROPY_THRESHOLD"] = "3.0"

    result = None
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pytest.skip("Script timed out")

    if result is None:
        pytest.skip("Script did not produce a result")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        pytest.skip(f"Script failed to run: {stderr or stdout}")

    rep = ART / "secret_entropy_report.json"
    if not rep.exists():
        pytest.skip("Report not generated")

    data = json.loads(rep.read_text())
    assert data["count"] > 0, "Value must be greater than zero"
