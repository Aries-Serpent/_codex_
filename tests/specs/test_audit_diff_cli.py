from __future__ import annotations

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
    try:
        import jinja2  # noqa: F401

        import yaml  # noqa: F401
    except Exception:
        pytest.skip("pyyaml/jinja2 not installed in test env")

    # Ensure at least one scoring file exists
    out = _run([str(runner), "stage", "S1"])
    assert out.returncode == 0
    out = _run([str(runner), "stage", "S2"])
    assert out.returncode == 0
    out = _run([str(runner), "stage", "S3"])
    assert out.returncode == 0
    out = _run([str(runner), "stage", "S4"])
    assert out.returncode == 0

    scored = Path("audit_artifacts/capabilities_scored.json")
    cp = _run([str(runner), "diff", "--old", str(scored), "--new", str(scored)])
    assert cp.returncode == 0, cp.stderr
    assert "ID,OLD,NEW,DELTA" in cp.stdout
