#!/usr/bin/env python3
"""
scan_failing_workflows.py — Grounded HEAD-SHA workflow scanner (P6-A, S295).

At Copilot session start, call this script to get an immediate picture of:
  1. All FAILED/CANCELLED check runs on HEAD_SHA
  2. All IN_PROGRESS check runs with ETA (based on median of last 10 runs)
  3. Workflows with ETA < 40 min flagged as "monitor while fixing"

Exit codes:
  0  — scan succeeded (even if there are failures; failures are in stdout)
  1  — GitHub API error (bad token / network)

Usage:
  python scripts/ci/scan_failing_workflows.py --sha <SHA> [--pr <N>] [--json]

Output (default markdown table):
  | Status | Workflow | Run | ETA/Duration | Action |
  ...

Environment:
  GH_TOKEN  — GitHub PAT with repo read scope (falls back to GITHUB_TOKEN)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_OWNER = "Aries-Serpent"
_REPO = "_codex_"
_ETA_MONITOR_THRESHOLD_MINUTES = 40
_HISTORY_RUNS = 10  # runs to average for ETA


# ── helpers ──────────────────────────────────────────────────────────────────

def _token() -> str:
    for var in ("GH_TOKEN", "GITHUB_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"):
        t = os.environ.get(var, "")
        if t:
            return t
    return ""


def _get(url: str, token: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        print(f"::error::GitHub API {exc.code} for {url}: {exc.read()[:200]}", file=sys.stderr)
        return None


def _paginate_check_runs(owner: str, repo: str, sha: str, token: str) -> list[dict]:
    """Fetch all check runs for a SHA (handles 100-item pages)."""
    runs: list[dict] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/check-runs"
            f"?per_page=100&page={page}"
        )
        data = _get(url, token)
        if not data or "check_runs" not in data:
            break
        batch = data["check_runs"]
        runs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return runs


def _workflow_runs_history(
    owner: str, repo: str, workflow_name: str, token: str, limit: int = _HISTORY_RUNS
) -> list[dict]:
    """Fetch recent completed workflow runs matching a name (for ETA estimation)."""
    url = (
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        f"?status=completed&per_page={limit}"
    )
    data = _get(url, token)
    if not data:
        return []
    return [r for r in data.get("workflow_runs", []) if r.get("name") == workflow_name]


def _median_duration_seconds(runs: list[dict]) -> float | None:
    """Compute median run duration (seconds) from completed runs."""
    durations = []
    for r in runs:
        created = r.get("created_at") or r.get("run_started_at")
        updated = r.get("updated_at")
        if created and updated:
            try:
                t0 = datetime.fromisoformat(created.replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                durations.append((t1 - t0).total_seconds())
            except ValueError:
                logger.debug("Suppressed exception in handler", exc_info=True)
    if not durations:
        return None
    durations.sort()
    mid = len(durations) // 2
    return durations[mid]


def _eta_minutes(run: dict, median_seconds: float | None) -> str:
    """Return ETA string for an in-progress run."""
    if median_seconds is None:
        return "unknown"
    started_raw = run.get("started_at") or run.get("created_at") or ""
    if not started_raw:
        return "unknown"
    try:
        started = datetime.fromisoformat(started_raw.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    remaining = median_seconds - elapsed
    if remaining <= 0:
        return "~finishing"
    mins = int(remaining / 60)
    return f"~{mins} min"


# ── main scan ─────────────────────────────────────────────────────────────────

def scan(
    owner: str,
    repo: str,
    sha: str,
    token: str,
    monitor_threshold: int = _ETA_MONITOR_THRESHOLD_MINUTES,
) -> dict:
    """
    Returns a dict with keys:
      failing   — list of failed/cancelled check-run summaries
      in_progress — list of in-progress summaries with ETA
      monitor   — subset of in_progress with ETA < threshold
      sha       — the scanned SHA
      summary   — human-readable markdown table
    """
    check_runs = _paginate_check_runs(owner, repo, sha, token)
    if check_runs is None:
        return {"error": "API failure", "failing": [], "in_progress": [], "monitor": []}

    failing = []
    in_progress_items = []

    for run in check_runs:
        name = run.get("name", "unknown")
        status = run.get("status", "")
        conclusion = run.get("conclusion") or ""
        url = run.get("html_url", "")
        run_id = run.get("id", "")

        if status == "completed" and conclusion not in ("success", "neutral", "skipped"):
            failing.append(
                {
                    "name": name,
                    "conclusion": conclusion,
                    "url": url,
                    "run_id": run_id,
                }
            )
        elif status in ("in_progress", "queued", "waiting", "requested"):
            # Estimate ETA from history
            history = _workflow_runs_history(owner, repo, name, token)
            median = _median_duration_seconds(history)
            eta_str = _eta_minutes(run, median)
            eta_minutes = None
            if eta_str.startswith("~") and "min" in eta_str:
                try:
                    eta_minutes = int(eta_str.replace("~", "").replace(" min", ""))
                except ValueError:
                    logger.debug("Suppressed exception in handler", exc_info=True)
            entry = {
                "name": name,
                "status": status,
                "url": url,
                "run_id": run_id,
                "eta": eta_str,
                "eta_minutes": eta_minutes,
                "median_duration_s": int(median) if median else None,
            }
            in_progress_items.append(entry)

    monitor = [
        r for r in in_progress_items
        if r["eta_minutes"] is not None and r["eta_minutes"] < monitor_threshold
    ]

    # Build markdown summary
    lines = [
        f"### 🔍 HEAD SHA `{sha[:12]}` — Workflow Status",
        "",
    ]

    if failing:
        lines.append(f"**❌ {len(failing)} failing check(s):**")
        lines.append("")
        lines.append("| Workflow | Conclusion | Run |")
        lines.append("|----------|-----------|-----|")
        for f in failing:
            lines.append(
                f"| `{f['name']}` | {f['conclusion']} | [#{f['run_id']}]({f['url']}) |"
            )
        lines.append("")
    else:
        lines.append("**✅ No failing checks.**")
        lines.append("")

    if in_progress_items:
        lines.append(
            f"**⏳ {len(in_progress_items)} in-progress "
            f"({'🔔 ' + str(len(monitor)) + ' monitored' if monitor else 'none < 40 min'}):**"
        )
        lines.append("")
        lines.append("| Workflow | Status | ETA | Monitor? |")
        lines.append("|----------|--------|-----|----------|")
        for ip in in_progress_items:
            flag = "🔔 YES" if ip in monitor else "—"
            lines.append(
                f"| `{ip['name']}` | {ip['status']} | {ip['eta']} | {flag} |"
            )
        lines.append("")

        if monitor:
            names = ", ".join(f"`{m['name']}`" for m in monitor)
            lines.append(
                f"> **⚠️ Monitor while fixing:** {names} — "
                f"complete in < {monitor_threshold} min. "
                f"Re-scan after fixing to verify they passed."
            )
            lines.append("")

    summary = "\n".join(lines)
    return {
        "sha": sha,
        "failing": failing,
        "in_progress": in_progress_items,
        "monitor": monitor,
        "summary": summary,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Scan failing/in-progress workflows for HEAD SHA")
    parser.add_argument("--sha", required=True, help="HEAD commit SHA to scan")
    parser.add_argument("--owner", default=_OWNER)
    parser.add_argument("--repo", default=_REPO)
    parser.add_argument("--pr", help="PR number (informational only)")
    parser.add_argument(
        "--threshold",
        type=int,
        default=_ETA_MONITOR_THRESHOLD_MINUTES,
        help="ETA threshold (minutes) for 'monitor while fixing' flag",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    args = parser.parse_args()

    token = _token()
    if not token:
        print("::error::No GitHub token found. Set GH_TOKEN or GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)

    result = scan(args.owner, args.repo, args.sha, token, args.threshold)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(result["summary"])
        if result.get("failing"):
            sys.exit(0)  # non-zero would confuse callers; failures are in output


if __name__ == "__main__":
    main()
