"""
P3 Test: Prefix Enforcement Validator

- Creates files in audit_artifacts/bundles with and without allowed prefixes.
- Ensures the validator reports violations.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
BUNDLES = ROOT / "audit_artifacts" / "bundles"
REPORT = ROOT / "audit_artifacts" / "prefix_validation_report.json"


def setup_files():
    if BUNDLES.exists():
        shutil.rmtree(BUNDLES.parent)
    BUNDLES.mkdir(parents=True)
    # Allowed
    (BUNDLES / "bundle_20250101.tar.gz").write_bytes(b"ok")
    (BUNDLES / "har_20250101.json").write_text("{}", encoding="utf-8")
    # Violation
    (BUNDLES / "foo_20250101.zip").write_bytes(b"x")


def test_prefix_validator_reports_violation():
    setup_files()
    env = os.environ.copy()
    env["BUNDLE_PREFIX_MODE"] = "1"
    subprocess.run(
        [sys.executable, "scripts/archive/validate_prefixes.py", "--warn-only"],
        check=True,
        env=env,
    )
    assert REPORT.exists(), "Condition must be true"
    data = json.loads(REPORT.read_text())
    assert len(data["violations"]) == 1, "Collection must not be empty"
    assert data["allowed"] == ["patchset_", "bundle_", "har_"]
