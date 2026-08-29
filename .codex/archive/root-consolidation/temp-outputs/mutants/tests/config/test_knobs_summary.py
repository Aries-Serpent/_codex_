"""
Knobs Summary Sidecar Test (P5)
Ensures knobs_effective.json produced when SUMMARY_ENABLE=1
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def test_knobs_summary_sidecar():
    env = os.environ.copy()
    env["SUMMARY_ENABLE"] = "1"
    # Minimal artifacts for manifest
    Path("audit_artifacts").mkdir(exist_ok=True)
    Path("audit_artifacts/capabilities_scored.json").write_text(
        json.dumps({"capabilities": []}), encoding="utf-8"
    )
    Path("audit_artifacts/context_index.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )
    subprocess.run(
        [sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S7"],
        check=True,
        env=env,
    )
    sidecar = Path("audit_artifacts/knobs_effective.json")
    assert sidecar.exists(), "knobs_effective.json sidecar missing"
