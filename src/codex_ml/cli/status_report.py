"""
codex_ml.cli.status_report

Summarize local readiness for promotion from a training run directory.

This is consumed by Engineering, Product, and Infra reviewers before merging
`0D_base_` → `main`. It relies ONLY on local artifacts produced by the TrainLoop
after training finishes:

  - run_metadata.json        (rollout_ring, owner, knobs)
  - reasoning.json           (reasoning harness summary, if any)
  - evaluation.json          (evaluation harness summary, if any)

We intentionally DO NOT reach out to any remote service.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def _load_json_if_exists(p: Path) -> Optional[dict[str, Any]]:
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_status_report(run_metadata_dir: Path) -> dict[str, Any]:
    """
    Collate readiness data for reviewers.

    Returns a dict shaped for human consumption and for PR templates.
    """
    meta = _load_json_if_exists(run_metadata_dir / "run_metadata.json") or {}
    reasoning = _load_json_if_exists(run_metadata_dir / "reasoning.json") or {}
    evaluation = _load_json_if_exists(run_metadata_dir / "evaluation.json") or {}

    knobs = meta.get("knobs", {})

    # Compute simple readiness signals
    rollout_ring = meta.get("rollout_ring")
    deployment_preset = knobs.get("deployment_preset")
    evaluation_preset = knobs.get("evaluation_preset")

    readiness = {
        "has_rollout_ring": bool(rollout_ring),
        "has_deployment_preset": bool(deployment_preset),
        "has_evaluation_preset": bool(evaluation_preset),
        # In future rings we can parse evaluation.json to verify pass/fail.
    }

    return {
        "rollout_ring": rollout_ring,
        "owner": meta.get("owner"),
        "knobs": knobs,
        "evaluation_summary": evaluation,
        "reasoning_summary": reasoning,
        "readiness_flags": readiness,
        "notes": (
            "All data is offline-local. Attach this JSON (or its path) to the PR "
            "requesting promotion to main."
        ),
    }
