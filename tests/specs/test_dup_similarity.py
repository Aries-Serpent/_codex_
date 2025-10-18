from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from tests.specs._workflow_config_utils import temporary_workflow_config


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

    def enable_token_similarity(cfg: dict[str, Any]) -> None:
        cfg.setdefault("scoring", {}).setdefault("dup", {})["heuristic"] = "token_similarity"

    with temporary_workflow_config(yaml, enable_token_similarity):  # type: ignore[name-defined]
        # Run S4 to ensure no crash; correctness of similarity is separately validated
        cp = _run([str(runner), "stage", "S4"])
        assert cp.returncode == 0, f"S4 failed: {cp.stderr}"

        # Basic sanity: scored file exists
        scored_path = Path("audit_artifacts") / "capabilities_scored.json"
        assert scored_path.exists()
        data = json.loads(scored_path.read_text(encoding="utf-8"))
        assert isinstance(data.get("capabilities"), list)
