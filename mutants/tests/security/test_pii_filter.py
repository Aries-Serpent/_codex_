"""
P2 Test: PII Filter (full modes)

Scenarios:
- allowlist only (baseline)
- minimal PII redaction (email pattern)
- extended union (AWS key + UUID)
- custom replace mode
- invalid regex handling (skip-manifest)

NOTE: Creates temporary artifacts in audit_artifacts/; does not modify originals (redacted sidecars).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART_DIR = Path("audit_artifacts")


def setup_artifacts():
    if ART_DIR.exists():
        shutil.rmtree(ART_DIR)
    ART_DIR.mkdir()
    (ART_DIR / "sample.md").write_text(
        "Contact: test@example.com UUID: 123e4567-e89b-12d3-a456-426614174000 KEY: AKIAABCDEFGHIJKLMNOP",
        encoding="utf-8",
    )
    (ART_DIR / "code.py").write_text(
        "token = 'ABCDEF1234567890ABCD' # seed usage seed", encoding="utf-8"
    )
    (ART_DIR / "ignore.bin").write_bytes(b"\x00\x01\x02")


def run_env(env_overrides):
    env = os.environ.copy()
    env.update(env_overrides)
    subprocess.run([sys.executable, "scripts/content_filter/apply_filter.py"], check=True, env=env)


def load_report():
    return json.loads((ART_DIR / "content_filter_report.json").read_text())


def test_allowlist_baseline():
    setup_artifacts()
    run_env({"CONTENT_FILTER_MODE": "allowlist", "ALLOWLIST_PROFILE": "A"})
    rep = load_report()
    assert rep["mode"] == "allowlist", "Condition must be true"
    assert rep["pii_redactions"] == 0, "Condition must be true"


def test_minimal_pii_redaction():
    setup_artifacts()
    run_env(
        {"CONTENT_FILTER_MODE": "pii", "PII_PATTERN_SET": "minimal", "PII_MODE": "union-minimal"}
    )
    rep = load_report()
    assert rep["mode"] == "pii", "Condition must be true"
    assert rep["pii_redactions"] >= 1, "Value must be greater than zero"
    # Ensure redacted sidecar created
    sidecar = Path("audit_artifacts/sample.md.redacted")
    assert sidecar.exists(), "Condition must be true"
    assert "<REDACT:" in sidecar.read_text(), "Condition must be true"


def test_extended_union():
    setup_artifacts()
    run_env(
        {"CONTENT_FILTER_MODE": "pii", "PII_PATTERN_SET": "extended", "PII_MODE": "union-extended"}
    )
    rep = load_report()
    assert rep["pii_redactions"] >= 3, "Value must be greater than zero"
    patterns_applied = rep["pii_patterns_applied"]
    assert any("AKIA" in p for p in patterns_applied), "Condition must be true"


def test_custom_replace():
    setup_artifacts()
    run_env(
        {
            "CONTENT_FILTER_MODE": "pii",
            "PII_PATTERN_SET": "minimal",
            "PII_MODE": "replace",
            "PII_CUSTOM_LIST": r"\bseed\b",
        }
    )
    rep = load_report()
    assert rep["pii_redactions"] >= 1, "Value must be greater than zero"
    assert any(p == r"\bseed\b" for p in rep["pii_patterns_applied"]), "p is not valid"


def test_invalid_regex_skip_manifest():
    setup_artifacts()
    run_env(
        {
            "CONTENT_FILTER_MODE": "pii",
            "PII_CUSTOM_LIST": "(unclosed",
            "PII_MODE": "union-minimal",
            "PII_REGEX_STRATEGY": "skip-manifest",
        }
    )
    rep = load_report()
    assert rep["invalid_patterns"], "Condition must be true"
    assert any(w.startswith("invalid_regex") for w in rep["warnings"]), "Condition must be true"
