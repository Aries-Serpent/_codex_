"""
Test Gaps Analyze

Test module for gaps analyze.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path("tools/gaps_analyze.py")


@pytest.mark.skipif(not TOOL.exists(), reason="gaps analyzer tool missing")
def test_gaps_analyzer_produces_output(tmp_path, monkeypatch):
    # Create a minimal scored input
    scored = {
        "capabilities": [
            {"name": "Security", "severity": 5, "confidence": 3, "weight": 0.2},
            {"name": "Tokenization", "severity": 3, "confidence": 5, "weight": 0.1},
        ]
    }
    in_path = tmp_path / "capabilities_scored.json"
    out_path = tmp_path / "gaps.json"
    in_path.write_text(json.dumps(scored), encoding="utf-8")
    code = subprocess.call(
        [
            sys.executable,
            str(TOOL),
            "--scored",
            str(in_path),
            "--out",
            str(out_path),
            "--maturity-threshold",
            "0.8",
        ]
    )
    assert code == 0, "code is not valid"
    assert out_path.exists(), "Condition must be true"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "items" in data and isinstance(data["items"], list)
    # Expect at least one flagged item
    assert len(data["items"]) >= 1, "Collection must not be empty"
