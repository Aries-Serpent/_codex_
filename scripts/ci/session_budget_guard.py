#!/usr/bin/env python3
"""Session Budget Guard — pre-flight check before starting a Copilot Cloud Agent session.

Prevents the rate-limit cascade (observed in PR #4389, runs 3476–3489) by:
  1. Estimating the API call cost of the pending task list
  2. Checking the local checkpoint for remaining weekly budget signals
  3. Warning when a session looks too large for the remaining budget
  4. Recommending task-splitting strategies when cost exceeds safe thresholds

Cost model
----------
Each Copilot agent session consumes tokens from the weekly budget.  GitHub
does not expose the remaining budget via API, so we use a conservative
heuristic based on observed session sizes and failure patterns:

  - SMALL  task   ≈  1–2 file edits, ≤3 tool calls       → LOW risk
  - MEDIUM task   ≈  3–10 file edits, 4–15 tool calls     → MEDIUM risk
  - LARGE  task   ≈  10+ files, parallel validation, etc.  → HIGH risk
  - HEAVY  session ≈ full PR rescue (20+ tool calls)       → VERY HIGH risk

If the checkpoint records a recent 429 with < 2h since reset, the guard
blocks session start.

Usage
-----
    # Check before starting a session
    python3 scripts/ci/session_budget_guard.py \
        --tasks "Fix CodeQL #13447,Resolve merge conflict,Update CHANGELOG" \
        --session S924

    # Non-zero exit if session is too large (use in CI pre-step)
    python3 scripts/ci/session_budget_guard.py --tasks "..." --assert-safe

    # Show estimate only (no exit code gate)
    python3 scripts/ci/session_budget_guard.py --tasks "..." --estimate-only

    # JSON output for CI consumption
    python3 scripts/ci/session_budget_guard.py --tasks "..." --json

Exit codes
----------
    0  Safe to start session
    1  High risk — recommend splitting or waiting
    2  BLOCKED — checkpoint shows rate limit not yet reset
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT_FILE = Path(".codex/rate_limit_checkpoint.json")
RATE_LIMIT_LOG = Path(".codex/rate_limit_log.jsonl")

# ── Cost heuristics (based on observed PR #4376, #4379, #4389 session sizes) ──

# Keywords in task names that indicate heavier work
_HEAVY_KEYWORDS = frozenset({
    "codeql", "security", "parallel_validation", "merge conflict",
    "resolve", "rebase", "rescue", "self-heal", "all alerts",
    "full test", "all issues", "comprehensive",
})
_MEDIUM_KEYWORDS = frozenset({
    "fix", "update", "changelog", "accountability", "pattern",
    "test", "workflow", "alert", "doc", "refactor",
})

# Estimated "token pressure units" (TPU) per task type (tuned to observed data)
_TPU = {
    "heavy": 25,   # Full session rescue, parallel_validation, all-alerts fix
    "medium": 10,  # Single fix, CHANGELOG update, single test
    "small": 4,    # Doc update, comment response, trivial rename
}

# Safety thresholds (TPU)
_THRESHOLD_WARN = 50    # Warn — session is getting large
_THRESHOLD_BLOCK = 100  # Block — very likely to hit rate limit


def _classify_task(task: str) -> str:
    t = task.lower()
    if any(kw in t for kw in _HEAVY_KEYWORDS):
        return "heavy"
    if any(kw in t for kw in _MEDIUM_KEYWORDS):
        return "medium"
    return "small"


def estimate_session_cost(tasks: list[str]) -> dict:
    """Estimate the token pressure of a list of tasks."""
    details = []
    total_tpu = 0
    for task in tasks:
        size = _classify_task(task)
        tpu = _TPU[size]
        total_tpu += tpu
        details.append({"task": task, "size": size, "tpu": tpu})

    risk = "low"
    if total_tpu >= _THRESHOLD_BLOCK:
        risk = "very_high"
    elif total_tpu >= _THRESHOLD_WARN:
        risk = "high"
    elif total_tpu >= _THRESHOLD_WARN // 2:
        risk = "medium"

    return {
        "total_tpu": total_tpu,
        "task_count": len(tasks),
        "risk_level": risk,
        "details": details,
        "warn_threshold": _THRESHOLD_WARN,
        "block_threshold": _THRESHOLD_BLOCK,
    }


def check_checkpoint_safety() -> dict:
    """Check the checkpoint file for rate-limit reset status."""
    if not CHECKPOINT_FILE.exists():
        return {"safe": True, "reason": "No prior rate-limit checkpoint"}

    try:
        cp = json.loads(CHECKPOINT_FILE.read_text())
    except Exception:
        return {"safe": True, "reason": "Checkpoint unreadable — assuming safe"}

    if cp.get("resolution") == "resolved":
        return {"safe": True, "reason": "Checkpoint is resolved — rate limit has recovered"}

    retry_after = cp.get("rate_limit", {}).get("retry_after_utc", "")
    if not retry_after or retry_after == "unknown":
        return {
            "safe": False,
            "blocked": False,
            "reason": (
                "Unresolved checkpoint with unknown reset time. "
                "Verify manually before starting."
            ),
            "checkpoint_session": cp.get("session", "?"),
        }

    try:
        reset_dt = datetime.strptime(retry_after, "%Y-%m-%dT%H:%MZ").replace(
            tzinfo=timezone.utc
        )
        now = datetime.now(timezone.utc)
        if now < reset_dt:
            mins_remaining = int((reset_dt - now).total_seconds() / 60)
            return {
                "safe": False,
                "blocked": True,
                "reason": (
                    f"Rate limit not yet reset. Retry in ~{mins_remaining} min "
                    f"({retry_after}). Session would immediately hit 429."
                ),
                "reset_at": retry_after,
                "mins_remaining": mins_remaining,
                "checkpoint_session": cp.get("session", "?"),
            }
        return {
            "safe": True,
            "reason": f"Reset window has passed ({retry_after}) — safe to retry",
        }
    except ValueError:
        return {
            "safe": False,
            "blocked": False,
            "reason": f"Could not parse retry_after_utc: {retry_after!r}",
        }


def split_suggestions(tasks: list[str], estimate: dict) -> list[list[str]]:
    """Suggest how to split a high-cost task list into safer sessions."""
    if estimate["risk_level"] in ("low", "medium"):
        return [tasks]

    sessions: list[list[str]] = []
    current: list[str] = []
    current_tpu = 0

    for detail in estimate["details"]:
        if current_tpu + detail["tpu"] > _THRESHOLD_WARN and current:
            sessions.append(current)
            current = []
            current_tpu = 0
        current.append(detail["task"])
        current_tpu += detail["tpu"]

    if current:
        sessions.append(current)

    return sessions if len(sessions) > 1 else [tasks]


def _print_report(tasks: list[str], estimate: dict, cp_check: dict, suggestions: list[list[str]]) -> None:  # noqa: E501
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    print(f"\n{'═'*60}")
    print(f"  🛡️  Session Budget Guard — {now}")
    print(f"{'═'*60}\n")

    # ── Cost estimate ─────────────────────────────────────────────
    risk_icons = {
        "low": "✅ LOW",
        "medium": "🟡 MEDIUM",
        "high": "🟠 HIGH",
        "very_high": "🔴 VERY HIGH",
    }
    risk = estimate["risk_level"]
    print("  📊 Session Cost Estimate")
    print(f"  {'─'*56}")
    print(f"  Risk level:   {risk_icons.get(risk, risk)}")
    print(f"  Total TPU:    {estimate['total_tpu']} / warn={estimate['warn_threshold']} / block={estimate['block_threshold']}")
    print(f"  Tasks ({estimate['task_count']}):")
    for d in estimate["details"]:
        size_icon = {"heavy": "🔴", "medium": "🟡", "small": "✅"}.get(d["size"], "?")
        print(f"     {size_icon} [{d['size']:<6}] {d['task']}")
    print()

    # ── Checkpoint safety ─────────────────────────────────────────
    print("  📋 Checkpoint Status")
    print(f"  {'─'*56}")
    safe_icon = "✅" if cp_check["safe"] else ("🔴" if cp_check.get("blocked") else "⚠️ ")
    print(f"  {safe_icon} {cp_check['reason']}")
    print()

    # ── Recommendation ────────────────────────────────────────────
    print("  💡 Recommendation")
    print(f"  {'─'*56}")

    if cp_check.get("blocked"):
        print("  🔴 BLOCKED — do NOT start session")
        print(f"     Rate limit resets in ~{cp_check.get('mins_remaining', '?')} min")
        print("     Then run: python3 scripts/ci/push_conflict_resolver.py")
        print("     Then run: python3 scripts/ci/rate_limit_handler.py --resolve")

    elif not cp_check["safe"]:
        print("  ⚠️  CAUTION — verify rate-limit reset before starting")

    elif risk == "very_high":
        print("  🟠 SPLIT RECOMMENDED — session likely to hit rate limit")
        for i, session_tasks in enumerate(suggestions, 1):
            print(f"     Session {i}:")
            for t in session_tasks:
                print(f"       • {t}")

    elif risk == "high":
        print("  🟡 LARGE SESSION — monitor for 429 errors mid-session")
        print("     Consider splitting heavy tasks into separate sessions")

    else:
        print("  ✅ Safe to start — session is within estimated budget")

    print(f"\n{'═'*60}\n")


# ── Entry point ────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--tasks",
        default="",
        help="Comma-separated list of planned tasks for this session",
    )
    p.add_argument(
        "--session",
        default="",
        help="Session identifier (e.g. S924)",
    )
    p.add_argument(
        "--assert-safe",
        action="store_true",
        help="Exit 1 if session is high-risk, exit 2 if blocked by checkpoint",
    )
    p.add_argument(
        "--estimate-only",
        action="store_true",
        help="Print estimate and always exit 0 (no gate)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    if not tasks:
        tasks = ["(no tasks specified — using default medium estimate)"]

    estimate = estimate_session_cost(tasks)
    cp_check = check_checkpoint_safety()
    suggestions = split_suggestions(tasks, estimate)

    if args.json_output:
        print(json.dumps({
            "session": args.session,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "estimate": estimate,
            "checkpoint_safety": cp_check,
            "split_suggestions": suggestions,
        }, indent=2))
        if args.estimate_only:
            return 0
    else:
        _print_report(tasks, estimate, cp_check, suggestions)

    if args.estimate_only:
        return 0

    if args.assert_safe:
        if cp_check.get("blocked"):
            return 2
        if estimate["risk_level"] in ("high", "very_high") or not cp_check["safe"]:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
