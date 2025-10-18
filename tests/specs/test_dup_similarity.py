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
def test_dup_heuristic_switch_fallback(tmp_path):
    """
    If token_similarity selected but module not available or fails, pipeline should fallback to simple heuristic.
    """
    runner = Path("scripts/space_traversal/audit_runner.py")
    if not runner.exists():
        pytest.skip("audit runner missing")
    try:
        import yaml  # noqa: F401
    except Exception:
        pytest.skip("pyyaml not installed")

    # S1..S3
    for stage in ("S1", "S2", "S3"):
        cp = _run([str(runner), "stage", stage])
        assert cp.returncode == 0, f"{stage} failed: {cp.stderr}"

    # Enable token_similarity in config
    cfg_path = Path(".copilot-space/workflow.yaml")
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))  # type: ignore[name-defined]
    cfg.setdefault("scoring", {}).setdefault("dup", {})["heuristic"] = "token_similarity"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")  # type: ignore[name-defined]

    # Run S4 to ensure no crash; correctness of similarity is separately validated
    cp = _run([str(runner), "stage", "S4"])
    assert cp.returncode == 0, f"S4 failed: {cp.stderr}"

    # Basic sanity: scored file exists
    scored_path = Path("audit_artifacts") / "capabilities_scored.json"
    assert scored_path.exists()
    data = json.loads(scored_path.read_text(encoding="utf-8"))
    assert isinstance(data.get("capabilities"), list)
