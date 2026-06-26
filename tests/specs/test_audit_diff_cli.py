"""
Test Audit Diff Cli

Test module for audit diff cli.
"""

from __future__ import annotations

import importlib.util
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
def test_audit_diff_cli_with_self(tmp_path):
    runner = Path("scripts/space_traversal/audit_runner.py")
    if not runner.exists():
        pytest.skip("audit runner missing")
    if importlib.util.find_spec("jinja2") is None or importlib.util.find_spec("yaml") is None:
        pytest.skip("pyyaml/jinja2 not installed in test env")

    # Ensure at least one scoring file exists
    out = _run(["-m", "scripts.space_traversal.audit_runner", "stage", "S1"])
    assert out.returncode == 0, "returncode is not valid"
    out = _run(["-m", "scripts.space_traversal.audit_runner", "stage", "S2"])
    assert out.returncode == 0, "returncode is not valid"
    out = _run(["-m", "scripts.space_traversal.audit_runner", "stage", "S3"])
    assert out.returncode == 0, "returncode is not valid"
    out = _run(["-m", "scripts.space_traversal.audit_runner", "stage", "S4"])
    assert out.returncode == 0, "returncode is not valid"

    scored = Path("audit_artifacts/capabilities_scored.json")
    cp = _run(
        [
            "-m",
            "scripts.space_traversal.audit_runner",
            "diff",
            "--old",
            str(scored),
            "--new",
            str(scored),
        ]
    )
    assert cp.returncode == 0, cp.stderr
    assert "ID,OLD,NEW,DELTA" in cp.stdout
