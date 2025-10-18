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
def test_meta_propagates_and_renders(tmp_path):
    """
    Verifies S3→S4 meta propagation and template rendering:
    - Ensures capabilities_scored.json carries 'meta' when present in raw.
    - Renders matrix and checks for 'Meta' section for a capability with meta.
    """
    runner = Path("scripts/space_traversal/audit_runner.py")
    if not runner.exists():
        pytest.skip("audit runner missing")

    # Optional deps for S6 template
    try:
        import jinja2  # noqa: F401

        import yaml  # noqa: F401
    except Exception:
        pytest.skip("pyyaml/jinja2 not installed in test env")

    # Run S1..S3
    for stage in ("S1", "S2", "S3"):
        cp = _run([str(runner), "stage", stage])
        assert cp.returncode == 0, f"{stage} failed: {cp.stderr}"

    # Inject meta into one raw capability (emulating a dynamic detector that adds meta)
    artifacts = Path("audit_artifacts")
    raw_path = artifacts / "capabilities_raw.json"
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    if not data.get("capabilities"):
        pytest.skip("no raw capabilities to annotate")
    data["capabilities"][0]["meta"] = {"layer": "test-meta", "owner": "qa"}
    raw_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # S4..S6
    for stage in ("S4", "S5", "S6"):
        cp = _run([str(runner), "stage", stage])
        assert cp.returncode == 0, f"{stage} failed: {cp.stderr}"

    # Check scored JSON
    scored = json.loads((artifacts / "capabilities_scored.json").read_text(encoding="utf-8"))
    cap0 = scored["capabilities"][0]
    assert "meta" in cap0 and cap0["meta"].get("layer") == "test-meta"

    # Check matrix render contains 'Meta' for that capability
    reports = Path("reports")
    latest = sorted(reports.glob("capability_matrix_*.md"))
    if not latest:
        pytest.skip("no report generated")
    text = latest[-1].read_text(encoding="utf-8")
    assert "Meta:" in text and "layer: test-meta" in text
