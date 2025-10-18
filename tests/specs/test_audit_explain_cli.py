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
def test_audit_explain_cli_smoke(tmp_path, monkeypatch):
    runner = Path("scripts/space_traversal/audit_runner.py")
    if not runner.exists():
        pytest.skip("audit runner missing")
    # Ensure YAML/template deps are installed in the environment running tests
    try:
        import jinja2  # noqa: F401

        import yaml  # noqa: F401
    except Exception:
        pytest.skip("pyyaml/jinja2 not installed in test env")

    # S1..S4 minimal path
    for stage in ("S1", "S2", "S3", "S4"):
        cp = _run([str(runner), "stage", stage])
        assert cp.returncode == 0, f"{stage} failed: {cp.stderr}"

    # Load a capability id to explain
    scored = json.loads(Path("audit_artifacts/capabilities_scored.json").read_text())
    caps = scored.get("capabilities", [])
    if not caps:
        pytest.skip("no capabilities scored; environment filtered everything")
    cap_id = caps[0]["id"]

    exp = _run([str(runner), "explain", cap_id])
    assert exp.returncode == 0, exp.stderr
    # Expect header and contribution lines
    assert f"Explain: {cap_id}" in exp.stdout
    assert "contribution=" in exp.stdout
