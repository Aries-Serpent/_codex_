#!/usr/bin/env python3
"""Bulk remediation orchestrator for the personalized Copilot campaign."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.ci.auto_fix_common_issues import CommonIssueFixer


def _utc_timestamp() -> str:
    """Return a UTC timestamp using the repository-standard format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_bulk_remediation(
    repo_root: Path,
    pattern: int | None = None,
    pattern_name: str | None = None,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run auto-fix patterns and return a structured execution summary."""

    fixer = CommonIssueFixer(repo_root=repo_root, check_only=False, dry_run=dry_run)
    if pattern is not None:
        fixer.run_all_patterns(pattern_num=pattern)
    elif pattern_name:
        fixer.run_all_patterns(pattern_name=pattern_name)
    else:
        fixer.run_all_patterns()

    report = fixer.generate_json_report()
    report["generated_at"] = _utc_timestamp()
    report["orchestrator"] = {
        "mode": "dry-run" if dry_run else "apply",
        "fixes_applied": fixer.fixes_applied,
        "blocking_issues_remaining": fixer.has_auto_fixable_issues(),
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main() -> None:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description="Run bulk CI remediation")
    parser.add_argument("--repo-root", default=".", help="Repository root to scan")
    parser.add_argument("--pattern", type=int, default=None, help="Pattern number to run")
    parser.add_argument(
        "--pattern-name",
        default=None,
        help="Pattern-name substring to run when --pattern is not supplied",
    )
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    parser.add_argument("--dry-run", action="store_true", help="Do not write fixes")
    args = parser.parse_args()

    report = run_bulk_remediation(
        repo_root=Path(args.repo_root).resolve(),
        pattern=args.pattern,
        pattern_name=args.pattern_name,
        output_path=Path(args.output).resolve() if args.output else None,
        dry_run=args.dry_run,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
