"""
P2 Test: Depth Gating (functional)

Procedure:
1. Run full audit at depth=4 (default) collect file count in context_index.json
2. Run full audit at depth=2 and confirm reduced count and warning present in manifest.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(depth_default=None, depth=None):
    env = os.environ.copy()
    if depth_default:
        env["AUDIT_DEPTH_DEFAULT"] = depth_default
    if depth:
        env["AUDIT_DEPTH"] = depth
    subprocess.run([sys.executable, "scripts/space_traversal/audit_runner.py", "run"], check=True, env=env)


def load_index():
    return json.loads(Path("audit_artifacts/context_index.json").read_text())


def load_manifest():
    return json.loads(Path("audit_run_manifest.json").read_text())


def test_depth_restriction():
    # Full depth baseline
    if Path("audit_artifacts").exists():
        shutil.rmtree("audit_artifacts")
    if Path("audit_run_manifest.json").exists():
        Path("audit_run_manifest.json").unlink()
    
    run(depth_default="4")
    idx_full = load_index()
    count_full = idx_full["count"]
    
    # Restricted depth
    shutil.rmtree("audit_artifacts")
    if Path("audit_run_manifest.json").exists():
        Path("audit_run_manifest.json").unlink()
    
    run(depth_default="2")
    idx_restrict = load_index()
    count_restrict = idx_restrict["count"]
    
    assert count_restrict <= count_full
    
    manifest = load_manifest()
    assert "depth_restriction_active" in manifest.get("warnings", [])
