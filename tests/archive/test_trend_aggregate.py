"""
Trend Aggregation Test (P5)
- Creates synthetic historical scored files
- Validates delta & sparkline inclusion
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
    ART.mkdir()
    for i, score in enumerate([0.5, 0.55, 0.60]):
        data = {
            "capabilities": [
                {"id": "alpha", "score": score},
                {"id": "beta", "score": 0.4 + i * 0.01},
            ]
        }
        (ART / f"capabilities_scored_{i}.json").write_text(json.dumps(data), encoding="utf-8")


def test_trend():
    setup()
    env = os.environ.copy()
    env["TREND_SPARKLINE"] = "1"
    subprocess.run([sys.executable, "scripts/archive/trend_aggregate.py"], check=True, env=env)
    out = ART / "trend_scores.json"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())
    alpha = next(c for c in data["capabilities"] if c["id"] == "alpha")
    assert alpha["delta"] > 0, "Value must be greater than zero"
    assert "sparkline" in alpha, "Condition must be true"
