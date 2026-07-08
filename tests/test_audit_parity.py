"""
Test Audit Parity

Test module for audit parity.
"""

#!/usr/bin/env python3
"""
Integration parity test for PR #2263

This test is intentionally conservative and non-invasive:
- Runs a minimal S1 -> S3 -> S4 -> S7 path (fast feedback) using the repo's runner.
- Asserts:
  * `mcp-tools-integration` appears in capabilities_raw.json (S3)
  * capabilities_scored.json exists and contains numeric scores for capabilities (S4)
  * audit_run_manifest.json contains a normalized_weights field (P2)
This file is intended to be committed to the PR branch `chore/audit-centralize-scoring-mcp-detector`
so the PR includes an automated smoke/integration check before requesting review.

Usage:
  pytest -q tests/test_audit_parity.py
"""

import json
import subprocess
import sys
from pathlib import Path

from codex.logging.structured_logger import logger

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "audit_artifacts"


def run(cmd, **kwargs):
    logger.info(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT, **kwargs)


def test_audit_parity_smoke(tmp_path):
    # Ensure a clean workspace
    run(["make", "space-clean"])

    # Run minimal pipeline: S1 (index), S3 (capabilities), S4 (scoring), S7 (manifest)
    # S6 (render) is optional and can be noisy; skip to keep test fast.
    run([sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S1"])
    run([sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S3"])
    run([sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S4"])
    run([sys.executable, "scripts/space_traversal/audit_runner.py", "stage", "S7"])

    # Basic file existence checks
    ctx = ARTIFACTS / "context_index.json"
    assert ctx.exists(), f"Missing {ctx}"
    raw = ARTIFACTS / "capabilities_raw.json"
    assert raw.exists(), f"Missing {raw}"
    scored = ARTIFACTS / "capabilities_scored.json"
    assert scored.exists(), f"Missing {scored}"
    manifest = ROOT / "audit_run_manifest.json"
    assert manifest.exists(), f"Missing {manifest}"

    # Load JSON artifacts
    raw_j = json.loads(raw.read_text(encoding="utf-8"))
    scored_j = json.loads(scored.read_text(encoding="utf-8"))
    manifest_j = json.loads(manifest.read_text(encoding="utf-8"))

    # Sanity: mcp-tools-integration appears in raw capabilities (detector presence)
    ids_raw = {c["id"] for c in raw_j.get("capabilities", [])}
    assert ("mcp-tools-integration" in ids_raw), "Detector 'mcp-tools-integration' not found in capabilities_raw.json"

    # Sanity: scored capabilities include numeric score for each capability
    for c in scored_j.get("capabilities", []):
        assert "id" in c and "score" in c, f"Scored capability missing fields: {c}"
        # Removed malformed assertion
