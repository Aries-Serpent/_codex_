"""CI Monitor Proactive skill handler.

Thin skill wrapper around ``scripts/ci/proactive_ci_monitor.py``.
Exposes the ``scan()`` function so the cognitive brain orchestrator can
trigger a proactive scan of open PRs for unhandled CI failures without
needing to shell out to the script directly.

Input schema
------------
{
  "repo": "owner/repo",
  "token": "<GitHub PAT>",
  "dry_run": false,
  "max_age_h": 2,
  "target_pr": 0,
  "min_confidence": 0.5
}

Output schema
-------------
{
  "status": "ok" | "error",
  "scanned_prs": 3,
  "failed_runs": 5,
  "escalated": 2,
  "skipped_transient": 1,
  "below_confidence": 0,
  "already_addressed": 2,
  "details": [...],
  "config": {...}
}
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPT = _REPO_ROOT / "scripts" / "ci" / "proactive_ci_monitor.py"


def _load_monitor_module() -> Any:
    if "proactive_ci_monitor" in sys.modules:
        return sys.modules["proactive_ci_monitor"]
    spec = importlib.util.spec_from_file_location("proactive_ci_monitor", _SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot locate proactive_ci_monitor at {_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["proactive_ci_monitor"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(payload: dict[str, Any]) -> dict[str, Any]:
    """Invoke a proactive CI scan.

    Parameters
    ----------
    payload:
        See module docstring for full input schema.

    Returns
    -------
    dict
        Scan report from ``proactive_ci_monitor.scan()``.
    """
    repo = payload.get("repo", "")
    token = payload.get("token", "")
    if not repo or not token:
        return {"status": "error", "message": "Missing required fields: repo, token"}

    dry_run = bool(payload.get("dry_run", True))
    max_age_h = int(payload.get("max_age_h", 2))
    target_pr = int(payload.get("target_pr", 0))
    min_confidence = float(payload.get("min_confidence", 0.5))

    try:
        mod = _load_monitor_module()
    except ImportError as exc:
        return {"status": "error", "message": f"proactive_ci_monitor unavailable: {exc}"}

    try:
        report = mod.scan(
            repo=repo,
            token=token,
            dry_run=dry_run,
            max_age_h=max_age_h,
            target_pr=target_pr,
            min_confidence=min_confidence,
        )
        report["status"] = "ok"
        return report
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
