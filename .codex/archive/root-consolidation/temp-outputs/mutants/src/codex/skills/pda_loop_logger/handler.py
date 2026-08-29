"""PDA Loop Logger skill handler.

Thin skill wrapper around ``scripts/ci/pda_failure_logger.py``.  Exposes
log-failure, log-fix, log-session, summarize, and query operations as a
single ``run(payload)`` entry-point so the cognitive brain can invoke the
PDA AfterMath store via the standard ``SkillRegistry``.

Input schema
------------
{
  "action": "log_failure" | "log_fix" | "log_session" | "summarize" | "query",

  // log_failure
  "session": "S293",
  "pr": 3854,
  "branch": "0D_base_",
  "pattern_id": "RP-PRECOMMIT-FAILURE",
  "workflow": "Validation Pipeline",
  "workflow_run": 23935948487,
  "error_text": "detect-secrets exit 3",
  "root_cause": "baseline stale",
  "fix_template": "pre-commit run detect-secrets --all-files",

  // log_fix
  "fix_applied": "Regenerated baseline",
  "verification_cmd": "pre-commit run detect-secrets --all-files",
  "verification_passed": true,

  // log_session  (all optional beyond session/pr)
  "summary": "Fixed 3 patterns",
  "commit": "abc1234",

  // summarize / query
  "pattern_id": "RP-007",   // optional filter
  "limit": 10
}

Output schema
-------------
{
  "status": "ok" | "error",
  "action": "<echoed>",
  "entries": [...],          // summarize / query only
  "entry": {...},            // log_* actions
  "message": "..."
}
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Bootstrap: locate pda_failure_logger.py at repo root
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[4]  # src/codex/skills/pda_loop_logger → repo root
_SCRIPT = _REPO_ROOT / "scripts" / "ci" / "pda_failure_logger.py"


def _load_logger_module() -> Any:
    """Dynamically import pda_failure_logger from scripts/ci/."""
    if "pda_failure_logger" in sys.modules:
        return sys.modules["pda_failure_logger"]
    spec = importlib.util.spec_from_file_location("pda_failure_logger", _SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot locate pda_failure_logger at {_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pda_failure_logger"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------


def run(payload: dict[str, Any]) -> dict[str, Any]:
    """Invoke the PDA Loop AfterMath logger.

    Parameters
    ----------
    payload:
        See module docstring for full input schema.

    Returns
    -------
    dict
        ``{"status": "ok"|"error", "action": ..., "message": ..., ...}``
    """
    action = payload.get("action", "")
    if not action:
        return {"status": "error", "message": "Missing required field: action"}

    try:
        logger_mod = _load_logger_module()
    except ImportError as exc:
        return {"status": "error", "message": f"pda_failure_logger unavailable: {exc}"}

    # ── Dispatch ────────────────────────────────────────────────────────────

    if action == "log_failure":
        return _log_failure(logger_mod, payload)
    if action == "log_fix":
        return _log_fix(logger_mod, payload)
    if action == "log_session":
        return _log_session(logger_mod, payload)
    if action == "summarize":
        return _summarize(logger_mod, payload)
    if action == "query":
        return _query(logger_mod, payload)
    return {"status": "error", "message": f"Unknown action: {action!r}"}


# ---------------------------------------------------------------------------
# Action implementations
# ---------------------------------------------------------------------------


def _log_failure(mod: Any, p: dict[str, Any]) -> dict[str, Any]:
    """Append a failure entry to the PDA JSONL store."""
    required = ["session", "pattern_id"]
    missing = [f for f in required if not p.get(f)]
    if missing:
        return {"status": "error", "message": f"Missing fields: {missing}"}

    entry = {
        "type": "failure",
        "session": p["session"],
        "pr": p.get("pr", 0),
        "branch": p.get("branch", ""),
        "pattern_id": p["pattern_id"],
        "workflow": p.get("workflow", ""),
        "workflow_run": p.get("workflow_run", ""),
        "error_text": p.get("error_text", ""),
        "root_cause": p.get("root_cause", ""),
        "fix_template": p.get("fix_template", ""),
        "ts": mod._now(),
    }
    mod._append_entry(entry)
    return {
        "status": "ok",
        "action": "log_failure",
        "entry": entry,
        "message": f"Logged failure pattern {entry['pattern_id']}",
    }


def _log_fix(mod: Any, p: dict[str, Any]) -> dict[str, Any]:
    """Append a fix-verification entry."""
    required = ["session", "pattern_id"]
    missing = [f for f in required if not p.get(f)]
    if missing:
        return {"status": "error", "message": f"Missing fields: {missing}"}

    entry = {
        "type": "fix",
        "session": p["session"],
        "pr": p.get("pr", 0),
        "pattern_id": p["pattern_id"],
        "fix_applied": p.get("fix_applied", ""),
        "verification_cmd": p.get("verification_cmd", ""),
        "verification_passed": bool(p.get("verification_passed", False)),
        "ts": mod._now(),
    }
    mod._append_entry(entry)
    return {
        "status": "ok",
        "action": "log_fix",
        "entry": entry,
        "message": f"Logged fix for {entry['pattern_id']} (passed={entry['verification_passed']})",
    }


def _log_session(mod: Any, p: dict[str, Any]) -> dict[str, Any]:
    """Append a session-completion summary entry."""
    entry = {
        "type": "session",
        "session": p.get("session", ""),
        "pr": p.get("pr", 0),
        "summary": p.get("summary", ""),
        "commit": p.get("commit", ""),
        "ts": mod._now(),
    }
    mod._append_entry(entry)
    return {
        "status": "ok",
        "action": "log_session",
        "entry": entry,
        "message": "Session summary logged",
    }


def _summarize(mod: Any, p: dict[str, Any]) -> dict[str, Any]:
    """Return grounded solutions ranked by success rate."""
    entries = mod._read_log()
    pattern_id_filter = p.get("pattern_id")
    limit = int(p.get("limit", 20))

    # Count successes per pattern
    from collections import defaultdict

    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "failures": 0,
            "fixes": 0,
            "success_rate": 0.0,
            "last_fix": "",
            "fix_templates": [],
        }
    )
    for e in entries:
        pid = e.get("pattern_id", "")
        if pattern_id_filter and pid != pattern_id_filter:
            continue
        if e.get("type") == "failure":
            stats[pid]["failures"] += 1
            tpl = e.get("fix_template", "")
            if tpl and tpl not in stats[pid]["fix_templates"]:
                stats[pid]["fix_templates"].append(tpl)
        elif e.get("type") == "fix" and e.get("verification_passed"):
            stats[pid]["fixes"] += 1
            stats[pid]["last_fix"] = e.get("ts", "")

    results = []
    for pid, s in stats.items():
        total = s["failures"]
        s["success_rate"] = round(s["fixes"] / total, 3) if total else 0.0
        s["pattern_id"] = pid
        results.append(s)

    results.sort(key=lambda x: (-x["fixes"], -x["success_rate"]))
    return {
        "status": "ok",
        "action": "summarize",
        "entries": results[:limit],
        "total_patterns": len(results),
    }


def _query(mod: Any, p: dict[str, Any]) -> dict[str, Any]:
    """Return raw log entries, optionally filtered by pattern_id or session."""
    entries = mod._read_log()
    pattern_id_filter = p.get("pattern_id")
    session_filter = p.get("session")
    limit = int(p.get("limit", 50))

    if pattern_id_filter:
        entries = [e for e in entries if e.get("pattern_id") == pattern_id_filter]
    if session_filter:
        entries = [e for e in entries if e.get("session") == session_filter]

    return {"status": "ok", "action": "query", "entries": entries[-limit:], "total": len(entries)}
