"""
Test Coverage End To End

Test module for coverage end to end.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = "scripts/space_traversal/coverage_ingest_stub.py"
FIXTURE = "tests/fixtures/sample_coverage.xml"


@pytest.mark.skipif(not Path(FIXTURE).exists(), reason="coverage fixture missing")
def test_coverage_ingest_end_to_end(tmp_path: Path):
    out_json = tmp_path / "audit_artifacts" / "coverage_mapped.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, SCRIPT, "--input", FIXTURE, "--out", str(out_json)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0, "returncode is not valid"
    assert out_json.exists(), "Condition must be true"
    with open(out_json, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict)
