#!/usr/bin/env python3
"""
Sync Issues To Report

Purpose:
    Synchronizes issues_to_report

Usage:
    python scripts/automation/sync_issues_to_report.py [options]

    Examples:
    $ python scripts/automation/sync_issues_to_report.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="Path to status report JSON to update")
    ap.add_argument("--issues", help="Path to issues JSON (pre-fetched)")
    ap.add_argument("--prs", help="Path to pull requests JSON (pre-fetched)")
    args = ap.parse_args(argv)

    report_path = Path(args.report)
    data = json.loads(report_path.read_text(encoding="utf-8"))

    automation = data.get("automation", {})
    if args.issues:
        issues = load_json(Path(args.issues))
        if issues is not None:
            automation["issues"] = issues
    if args.prs:
        prs = load_json(Path(args.prs))
        if prs is not None:
            automation["pull_requests"] = prs

    automation["synced_utc"] = datetime.now(timezone.utc).isoformat()
    data["automation"] = automation
    report_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] Updated automation fields in {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
