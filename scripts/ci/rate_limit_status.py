#!/usr/bin/env python3
"""Rate-Limit Status CLI — check current Copilot + GitHub API rate-limit state.

Provides three data sources in one command:
  1. GitHub REST API rate-limit endpoint (remaining requests, reset time)
  2. Local checkpoint file (.codex/rate_limit_checkpoint.json)
  3. Workflow run log scan — counts 429 hits in the last N runs

Usage
-----
    # Full status (all sources)
    python3 scripts/ci/rate_limit_status.py

    # JSON output for scripting
    python3 scripts/ci/rate_limit_status.py --json

    # Scan workflow runs for 429 patterns (requires GH_TOKEN)
    python3 scripts/ci/rate_limit_status.py --scan-runs 20

    # Watch mode — poll every 60s and alert when budget recovers
    python3 scripts/ci/rate_limit_status.py --watch --interval 60

    # Non-zero exit if any rate limit is exhausted (for CI gates)
    python3 scripts/ci/rate_limit_status.py --assert-ok

Exit codes
----------
    0  All limits healthy
    1  One or more limits exhausted or unknown
    2  Network / auth error
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────

CHECKPOINT_FILE = Path(".codex/rate_limit_checkpoint.json")
RATE_LIMIT_LOG = Path(".codex/rate_limit_log.jsonl")

GH_TOKEN = (
    os.environ.get("CODEX_MASTER_KEY")
    or os.environ.get("CODEX_BACKUP_KEY")
    or os.environ.get("GITHUB_TOKEN")
    or os.environ.get("GH_TOKEN")
    or ""
)
REPO = os.environ.get("GITHUB_REPOSITORY", "")

# Copilot weekly limit is not exposed via API — we infer from checkpoint history
# These constants come from GitHub's documentation + observed behaviour
COPILOT_WEEKLY_LIMIT_HINT = "Not publicly exposed — inferred from 429 history"


# ── GitHub API helper ──────────────────────────────────────────────────────────

def _gh_get(path: str) -> tuple[int, object]:
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-rate-limit-status/1.0",
    }
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except Exception as exc:
        return -1, {"error": str(exc)}


# ── Data sources ───────────────────────────────────────────────────────────────

def get_github_api_limits() -> dict:
    """Query GitHub REST API rate-limit endpoint."""
    status, data = _gh_get("/rate_limit")
    if status != 200:
        return {"error": f"HTTP {status}", "available": False}

    result = {"available": True, "resources": {}}
    resources = data.get("resources", {})  # type: ignore[union-attr]

    for name, info in resources.items():
        remaining = info.get("remaining", 0)
        limit = info.get("limit", 0)
        reset_ts = info.get("reset", 0)
        reset_dt = (
            datetime.fromtimestamp(reset_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
            if reset_ts
            else "unknown"
        )
        pct = int(100 * remaining / limit) if limit else 0
        result["resources"][name] = {
            "remaining": remaining,
            "limit": limit,
            "reset_utc": reset_dt,
            "pct_remaining": pct,
            "exhausted": remaining == 0,
            "warning": pct < 20 and remaining > 0,
        }

    # Top-level core summary
    core = result["resources"].get("core", {})
    result["summary"] = {
        "core_remaining": core.get("remaining", "?"),
        "core_limit": core.get("limit", "?"),
        "core_pct": core.get("pct_remaining", "?"),
        "core_reset": core.get("reset_utc", "?"),
        "any_exhausted": any(
            r.get("exhausted") for r in result["resources"].values()
        ),
    }
    return result


def get_checkpoint_status() -> dict:
    """Read the local rate-limit checkpoint file."""
    if not CHECKPOINT_FILE.exists():
        return {"found": False, "message": "No checkpoint file — no prior rate-limit interruption recorded."}

    try:
        cp = json.loads(CHECKPOINT_FILE.read_text())
    except Exception as exc:
        return {"found": True, "error": f"Corrupt checkpoint: {exc}"}

    resolution = cp.get("resolution", "pending")
    rl = cp.get("rate_limit", {})
    tasks = cp.get("tasks", {})
    pending_count = len(tasks.get("pending", []))
    in_prog_count = len(tasks.get("in_progress", []))

    return {
        "found": True,
        "resolved": resolution == "resolved",
        "resolution": resolution,
        "session": cp.get("session", "unknown"),
        "pr_number": cp.get("pr_number", "?"),
        "created_at": cp.get("created_at", "?"),
        "resolved_at": cp.get("resolved_at"),
        "request_id": rl.get("request_id", "?"),
        "retry_after_utc": rl.get("retry_after_utc", "?"),
        "reset_minutes": rl.get("reset_minutes"),
        "tasks_pending": pending_count,
        "tasks_in_progress": in_prog_count,
        "tasks_completed": len(tasks.get("completed", [])),
        "push_conflict_risk": bool(cp.get("push_conflict_risk")),
    }


def get_rate_limit_log_history(tail: int = 20) -> list[dict]:
    """Read the append-only rate-limit event log."""
    if not RATE_LIMIT_LOG.exists():
        return []
    entries = []
    malformed_count = 0
    try:
        lines = RATE_LIMIT_LOG.read_text().splitlines()
        for line in lines[-tail:]:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    # Keep tolerant behavior while tracking malformed NDJSON rows.
                    malformed_count += 1
    except Exception as exc:
        print(f"⚠️ Could not read rate-limit log history: {exc}", file=sys.stderr)
    if malformed_count:
        print(
            f"⚠️ Skipped {malformed_count} malformed rate-limit log "
            f"{'entry' if malformed_count == 1 else 'entries'}.",
            file=sys.stderr,
        )
    return entries


def scan_workflow_runs_for_429(limit: int = 20) -> dict:
    """Scan recent Copilot cloud agent workflow runs for 429 rate-limit hits."""
    if not REPO or not GH_TOKEN:
        return {"error": "GITHUB_REPOSITORY and GH_TOKEN required for run scanning"}

    status, data = _gh_get(
        f"/repos/{REPO}/actions/runs?per_page={limit}&event=dynamic"
    )
    if status != 200:
        return {"error": f"Could not list workflow runs (HTTP {status})"}

    runs = data.get("workflow_runs", [])  # type: ignore[union-attr]
    copilot_runs = [
        r for r in runs
        if "copilot" in r.get("name", "").lower()
        or "copilot" in r.get("display_title", "").lower()
    ]

    rate_limited = []

    for r in copilot_runs:
        conclusion = r.get("conclusion", "")
        run_id = r.get("id")
        created = r.get("created_at", "")
        branch = r.get("head_branch", "")
        if conclusion == "failure":
            # We can't read log content here without fetching jobs, but we track failures
            rate_limited.append({
                "run_id": run_id,
                "created_at": created,
                "branch": branch,
                "conclusion": conclusion,
                "url": r.get("html_url", ""),
            })

    return {
        "total_copilot_runs_scanned": len(copilot_runs),
        "failed_runs": len(rate_limited),
        "failed_run_details": rate_limited[:10],
        "note": (
            "Failed Copilot runs may be due to rate-limit OR push conflicts. "
            "Check .codex/rate_limit_checkpoint.json for 429 evidence."
        ),
    }


def append_rate_limit_event(event: dict) -> None:
    """Append a rate-limit event to the persistent log for trend analysis."""
    RATE_LIMIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("logged_at", datetime.now(timezone.utc).isoformat())
    with RATE_LIMIT_LOG.open("a") as f:
        f.write(json.dumps(event) + "\n")


# ── Display ────────────────────────────────────────────────────────────────────


def _bar(pct: int, width: int = 20) -> str:
    filled = int(width * pct / 100)
    return "█" * filled + "░" * (width - filled)


def print_status(api: dict, cp: dict, history: list, scan: dict | None) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    print(f"\n{'═'*60}")
    print(f"  📊 Rate-Limit Status — {now}")
    print(f"{'═'*60}\n")

    # ── GitHub REST API limits ────────────────────────────────────────
    print("  🌐 GitHub REST API Limits")
    print(f"  {'─'*56}")
    if api.get("error"):
        print(f"  ❌ Could not fetch: {api['error']}")
        if not GH_TOKEN:
            print("     → Set CODEX_MASTER_KEY or GH_TOKEN to enable API checks")
    elif api.get("available"):
        for name, info in api.get("resources", {}).items():
            pct = info.get("pct_remaining", 0)
            icon = "🔴" if info.get("exhausted") else ("⚠️ " if info.get("warning") else "✅")
            bar = _bar(pct)
            print(
                f"  {icon} {name:<18} {info['remaining']:>6}/{info['limit']:<6} "
                f"[{bar}] {pct:>3}%  resets {info['reset_utc']}"
            )
    print()

    # ── Copilot weekly limit (checkpoint-inferred) ─────────────────
    print("  🤖 Copilot Weekly Limit (inferred from checkpoint)")
    print(f"  {'─'*56}")
    if not cp.get("found"):
        print("  ✅ No checkpoint — no prior weekly rate-limit hit recorded")
    else:
        resolved = cp.get("resolved")
        icon = "✅" if resolved else "🔴"
        print(f"  {icon} Resolution:    {cp.get('resolution', 'unknown')}")
        print(f"     Session:       {cp.get('session', '?')} (PR #{cp.get('pr_number', '?')})")
        print(f"     Interrupted:   {cp.get('created_at', '?')}")
        if resolved:
            print(f"     Resolved at:   {cp.get('resolved_at', '?')}")
        else:
            print(f"     Retry after:   {cp.get('retry_after_utc', '?')}")
            print(f"     Tasks pending: {cp.get('tasks_pending', 0)}")
            print(f"     In-progress:   {cp.get('tasks_in_progress', 0)}")
            if cp.get("push_conflict_risk"):
                print("     ⚠️  Push conflict risk: run push_conflict_resolver.py first")
            print()
            print("  Recovery commands:")
            print("     python3 scripts/ci/push_conflict_resolver.py")
            print("     python3 scripts/ci/rate_limit_handler.py --resolve")
    print()

    # ── Event history ─────────────────────────────────────────────
    if history:
        print(f"  📜 Rate-Limit Event History (last {len(history)} entries)")
        print(f"  {'─'*56}")
        for e in history[-5:]:
            print(f"     {e.get('logged_at','?')[:19]}  {e.get('event','?')}")
        print()

    # ── Workflow run scan ─────────────────────────────────────────
    if scan:
        print("  🔍 Recent Copilot Agent Run Scan")
        print(f"  {'─'*56}")
        if scan.get("error"):
            print(f"  ⚠️  {scan['error']}")
        else:
            failed = scan.get("failed_runs", 0)
            total = scan.get("total_copilot_runs_scanned", 0)
            icon = "🔴" if failed > 3 else ("⚠️ " if failed > 0 else "✅")
            print(f"  {icon} {failed}/{total} Copilot runs failed (may include rate-limit + push conflicts)")
            for r in scan.get("failed_run_details", [])[:5]:
                print(f"     • Run {r['run_id']} — {r['created_at'][:16]} — {r['branch']}")
        print()

    print(f"{'═'*60}\n")


# ── Watch mode ─────────────────────────────────────────────────────────────────

def watch(interval: int, assert_ok: bool) -> None:
    print(f"👀 Watch mode — polling every {interval}s. Ctrl-C to stop.\n")
    try:
        while True:
            api = get_github_api_limits()
            cp = get_checkpoint_status()
            history = get_rate_limit_log_history()
            print_status(api, cp, history, None)

            # Check if Copilot checkpoint has recovered
            if cp.get("found") and not cp.get("resolved"):
                retry = cp.get("retry_after_utc", "")
                if retry and retry != "unknown":
                    try:
                        reset_dt = datetime.strptime(retry, "%Y-%m-%dT%H:%MZ").replace(
                            tzinfo=timezone.utc
                        )
                        if datetime.now(timezone.utc) >= reset_dt:
                            print("🟢 Rate-limit reset window has passed! Safe to retry.")
                    except ValueError as exc:
                        print(
                            "⚠️ Could not parse checkpoint retry_after_utc "
                            f"({retry!r}): {exc}; skipping reset-time check."
                        )

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Watch stopped.")


# ── Entry point ────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output full status as JSON",
    )
    p.add_argument(
        "--scan-runs",
        type=int,
        default=0,
        metavar="N",
        help="Scan last N Copilot workflow runs for failures (requires GH_TOKEN)",
    )
    p.add_argument(
        "--watch",
        action="store_true",
        help="Poll continuously until manually stopped",
    )
    p.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Poll interval in seconds for --watch (default: 60)",
    )
    p.add_argument(
        "--assert-ok",
        action="store_true",
        help="Exit 1 if any limit is exhausted or checkpoint is unresolved",
    )
    p.add_argument(
        "--log-event",
        type=str,
        default="",
        metavar="EVENT",
        help="Append a named event to .codex/rate_limit_log.jsonl (e.g. '429-hit')",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    if args.log_event:
        append_rate_limit_event({"event": args.log_event})
        print(f"✅ Logged event '{args.log_event}' to {RATE_LIMIT_LOG}")
        return 0

    if args.watch:
        watch(args.interval, args.assert_ok)
        return 0

    api = get_github_api_limits()
    cp = get_checkpoint_status()
    history = get_rate_limit_log_history()
    scan = scan_workflow_runs_for_429(args.scan_runs) if args.scan_runs > 0 else None

    if args.json_output:
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "github_api": api,
            "copilot_checkpoint": cp,
            "event_history": history[-10:],
        }
        if scan:
            output["workflow_scan"] = scan
        print(json.dumps(output, indent=2))
    else:
        print_status(api, cp, history, scan)

    # Determine exit code
    if args.assert_ok:
        exhausted = api.get("summary", {}).get("any_exhausted", False)
        checkpoint_unresolved = cp.get("found") and not cp.get("resolved")
        if exhausted or checkpoint_unresolved:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
