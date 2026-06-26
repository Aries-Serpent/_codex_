"""
Test Autodiscovery

Test module for autodiscovery.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("tools/capability_autodiscover.py")
OUT = Path("audit_artifacts/capabilities_raw.json")


@pytest.mark.skipif(not SCRIPT.exists(), reason="autodiscovery tool missing")
def test_autodiscovery_runs(tmp_path, monkeypatch):
    # Run the script and ensure it writes the output file
    subprocess.check_call([sys.executable, str(SCRIPT)])
    assert OUT.exists(), "Condition must be true"
    data = json.loads(OUT.read_text(encoding="utf-8"))
    assert "suggested_capabilities" in data, "Data must not be empty"
    assert isinstance(data["suggested_capabilities"], list)
