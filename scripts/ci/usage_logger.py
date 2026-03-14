#!/usr/bin/env python3
"""
T-004 — Actions Usage NDJSON Logger.

Appends one structured line per cost-gate run to `.codex/logs/usage.ndjson`
so that monthly Actions-minute consumption can be tracked locally.

The file is gitignored (`.codex/logs/` is in `.gitignore`).

Usage (called automatically by cost-gate.yml after every estimate):

    python scripts/ci/usage_logger.py \\
        --workflow "Build & Push Preview Image" \\
        --runner ubuntu-latest-m \\
        --effective-minutes 120 \\
        --tier RED \\
        --pr-number 3575

CLI arguments are all optional; missing values default to empty/0.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path

_LOG_PATH = Path(".codex/logs/usage.ndjson")


def log_usage(
    *,
    workflow: str,
    runner: str,
    effective_minutes: float,
    tier: str,
    pr_number: str = "",
    branch: str = "",
    sha: str = "",
    approved: bool | None = None,
) -> dict:
    """Append one NDJSON entry and return it."""
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry: dict = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "workflow": workflow,
        "runner": runner,
        "effective_minutes": round(effective_minutes, 2),
        "tier": tier,
    }
    if pr_number:
        entry["pr"] = pr_number
    if branch:
        entry["branch"] = branch
    if sha:
        entry["sha"] = sha[:12]
    if approved is not None:
        entry["approved"] = approved

    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    return entry


def monthly_summary(log_path: Path = _LOG_PATH) -> dict:
    """Return total effective_minutes logged this calendar month."""
    now = datetime.datetime.now(datetime.timezone.utc)
    month_prefix = now.strftime("%Y-%m")
    total_min = 0.0
    entries: list[dict] = []

    if not log_path.exists():
        return {"month": month_prefix, "total_minutes": 0.0, "entries": 0}

    with log_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("ts", "").startswith(month_prefix):
                total_min += float(rec.get("effective_minutes", 0))
                entries.append(rec)

    return {
        "month": month_prefix,
        "total_minutes": round(total_min, 2),
        "entries": len(entries),
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Log a cost-gate event to NDJSON")
    p.add_argument("--workflow", default="")
    p.add_argument("--runner", default="ubuntu-latest")
    p.add_argument("--effective-minutes", type=float, default=0.0)
    p.add_argument("--tier", default="GREEN", choices=["GREEN", "YELLOW", "RED"])
    p.add_argument("--pr-number", default=os.environ.get("PR_NUMBER", ""))
    p.add_argument("--branch", default=os.environ.get("GITHUB_REF_NAME", ""))
    p.add_argument("--sha", default=os.environ.get("GITHUB_SHA", ""))
    p.add_argument(
        "--approved",
        default=None,
        choices=["true", "false"],
        help="Whether stakeholder approved this run",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print monthly summary and exit (no new log entry)",
    )
    p.add_argument(
        "--budget-alert",
        action="store_true",
        help="Exit code 1 if this month's usage >= BUDGET_ALERT_THRESHOLD",
    )
    p.add_argument(
        "--budget-alert-threshold",
        type=float,
        default=2500.0,
        metavar="MINUTES",
        help="Alert threshold (default: 2500, i.e. 83%% of 3000 min/month budget)",
    )
    p.add_argument("--log-path", default=str(_LOG_PATH))
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    global _LOG_PATH  # noqa: PLW0603
    _LOG_PATH = Path(args.log_path)

    if args.summary or args.budget_alert:
        summary = monthly_summary(_LOG_PATH)
        print(json.dumps(summary, indent=2))
        if args.budget_alert:
            used = summary["total_minutes"]
            threshold = args.budget_alert_threshold
            if used >= threshold:
                print(
                    f"⚠️  BUDGET ALERT: {used:.0f} / 3000 min used this month "
                    f"(threshold: {threshold:.0f} min)",
                    flush=True,
                )
                return 1
        return 0

    approved: bool | None = None
    if args.approved == "true":
        approved = True
    elif args.approved == "false":
        approved = False

    entry = log_usage(
        workflow=args.workflow,
        runner=args.runner,
        effective_minutes=args.effective_minutes,
        tier=args.tier,
        pr_number=args.pr_number,
        branch=args.branch,
        sha=args.sha,
        approved=approved,
    )
    print(json.dumps(entry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
