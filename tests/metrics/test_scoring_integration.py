"""
Scoring Integration Test (P5)
Validates:
- Consistency incorporates similarity_index when token_similarity.json present
- Tests component elevated by coverage_percent
- Safeguards component influenced by severity factor (additive mode)
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")


def setup_base():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()
    # Minimal raw capability artifact
    capabilities = [
        {
            "id": "alpha",
            "evidence_files": ["a.py", "b.py"],
            "found_patterns": ["train"],
            "required_patterns": ["train", "epoch"],
        }
    ]
    (ART / "capabilities_raw.json").write_text(
        json.dumps({"capabilities": capabilities}, indent=2), encoding="utf-8"
    )
    Path("a.py").write_text("train epoch seed rng", encoding="utf-8")
    Path("b.py").write_text("train epoch seed rng", encoding="utf-8")  # duplicated content
    # Token similarity (makes similarity_index lower due to similarity)
    sim = {"capabilities": [{"id": "alpha", "similarity_index": 0.25, "files_considered": 2}]}
    (ART / "token_similarity.json").write_text(json.dumps(sim), encoding="utf-8")
    # Coverage stats (improves tests component)
    cov = {"capabilities": [{"id": "alpha", "coverage_percent": 0.90}]}
    (ART / "coverage_stats.json").write_text(json.dumps(cov), encoding="utf-8")
    # Security severity (improves safeguards)
    sev = {
        "counts": {"high": 1, "medium": 0, "low": 0, "total": 1},
        "weights": {"high": 0.05, "medium": 0.02, "low": 0.01},
    }
    (ART / "security_severity.json").write_text(json.dumps(sev), encoding="utf-8")


def test_scoring_enhancements():
    setup_base()
    env = os.environ.copy()
    env["TOKEN_SIMILARITY_ENABLE"] = "1"
    env["COVERAGE_ENABLE"] = "1"
    env["SECURITY_SEVERITY_ENABLE"] = "1"
    env["SEVERITY_MULTIPLIER_MODE"] = "additive"
    # Need workflow.yaml present; assume existing root file
    subprocess.run(
        [sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S4"],
        check=True,
        env=env,
    )
    scored = json.loads((ART / "capabilities_scored.json").read_text())["capabilities"][0]
    comps = scored["components"]
    assert comps["tests"] >= 0.80, "Coverage percent not applied to tests component"
    # Consistency should reflect duplication * similarity scaling
    assert comps["consistency"] < 1.0, "Consistency did not integrate similarity"
    # Safeguards elevated by severity factor
    assert comps["safeguards"] > 0.0, "Value must be greater than zero"
