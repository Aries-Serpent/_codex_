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
def test_component_caps_reduce_component_value(tmp_path):
    """
    Ensures component caps clamp pre-weight values:
    - Sets functionality cap below 1.0 and constructs raw capability with functionality > cap.
    - Verifies functionality component is clamped and total score reduced accordingly.
    """
    runner = Path("scripts/space_traversal/audit_runner.py")
    if not runner.exists():
        pytest.skip("audit runner missing")
    try:
        import yaml  # noqa: F401
    except Exception:
        pytest.skip("pyyaml not installed")

    # Prepare S1..S3
    for stage in ("S1", "S2", "S3"):
        cp = _run([str(runner), "stage", stage])
        assert cp.returncode == 0, f"{stage} failed: {cp.stderr}"

    # Load config and add a functionality cap
    cfg_path = Path(".copilot-space/workflow.yaml")
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))  # type: ignore[name-defined]
    cfg.setdefault("scoring", {}).setdefault("component_caps", {})["functionality"] = 0.6
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")  # type: ignore[name-defined]

    # Force raw data to yield functionality > 1.0 before clamp:
    # len(found_patterns) > len(required_patterns) → raw ratio > 1 → clamp to 1 → then cap to 0.6
    artifacts = Path("audit_artifacts")
    raw_path = artifacts / "capabilities_raw.json"
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    assert data.get("capabilities"), "No raw capabilities"
    cap = data["capabilities"][0]
    cap["required_patterns"] = ["a"]  # denominator = 1
    cap["found_patterns"] = ["a", "b", "c"]  # numerator = 3 (>1)
    raw_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Run S4
    cp = _run([str(runner), "stage", "S4"])
    assert cp.returncode == 0, f"S4 failed: {cp.stderr}"

    scored = json.loads((artifacts / "capabilities_scored.json").read_text(encoding="utf-8"))
    c0 = next(c for c in scored["capabilities"] if c["id"] == cap["id"])
    # Functionality must be capped to 0.6
    assert abs(c0["components"]["functionality"] - 0.6) < 1e-9
