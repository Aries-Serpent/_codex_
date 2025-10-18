from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


@pytest.mark.smoke
def test_manifest_contains_integrity_chain_and_weights(tmp_path):
    runner = Path("scripts/space_traversal/audit_runner.py")
    if not runner.exists():
        pytest.skip("audit runner missing")
    # Dependencies are optional
    try:
        import jinja2  # noqa: F401

        import yaml  # noqa: F401
    except Exception:
        pytest.skip("pyyaml/jinja2 not installed in test env")

    # Run S1..S7
    for stage in ("S1", "S2", "S3", "S4", "S5", "S6", "S7"):
        cp = _run([str(runner), "stage", stage])
        assert cp.returncode == 0, f"{stage} failed: {cp.stderr}"

    # Validate manifest
    mf = Path("audit_run_manifest.json")
    assert mf.exists(), "Manifest should exist after S7"
    data = json.loads(mf.read_text())
    # Integrity fields
    assert (
        isinstance(data.get("repo_root_sha"), str) and data["repo_root_sha"]
    ), "repo_root_sha missing"
    assert (
        isinstance(data.get("template_hash"), str) and data["template_hash"]
    ), "template_hash missing"
    assert isinstance(data.get("artifacts"), list) and data["artifacts"], "artifacts missing"
    # Weights and warnings
    assert isinstance(data.get("weights"), dict) and data["weights"], "weights missing"
    assert isinstance(data.get("warnings"), list), "warnings should be a list"
