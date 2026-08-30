"""
P3 Test: Manifest Warning Aggregation

- Writes content_filter_report.json with warnings
- Writes a bundles pointer JSON with warnings
- Runs stage S7 and verifies audit_run_manifest.json includes aggregated warnings
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ART = Path("audit_artifacts")
BUNDLES = ART / "bundles"


def setup():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir(parents=True)
    # Minimal artifacts for manifest hashing
    (ART / "context_index.json").write_text(
        json.dumps({"version": "1.0", "files": []}), encoding="utf-8"
    )
    (ART / "capabilities_scored.json").write_text(
        json.dumps({"capabilities": []}), encoding="utf-8"
    )
    # Content filter report
    (ART / "content_filter_report.json").write_text(
        json.dumps({"mode": "pii", "warnings": ["invalid_regex:1"], "invalid_patterns": ["("]}),
        encoding="utf-8",
    )
    # Pointer with warnings
    BUNDLES.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    (BUNDLES / f"bundle_{stamp}.pointer.json").write_text(
        json.dumps({"warnings": ["pointer_style_degraded:embedded"]}), encoding="utf-8"
    )


def test_manifest_collects_external_warnings():
    setup()
    # Run stage S7 only; requires workflow config to resolve paths (assumed present)
    env = os.environ.copy()
    subprocess.run(
        [sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S7"],
        check=True,
        env=env,
    )
    mpath = Path("audit_run_manifest.json")
    assert mpath.exists(), "Condition must be true"
    mf = json.loads(mpath.read_text())
    warns = mf.get("warnings", [])
    assert any("invalid_regex" in w for w in warns), "Condition must be true"
    assert any("pointer_style_degraded" in w for w in warns), "Condition must be true"
