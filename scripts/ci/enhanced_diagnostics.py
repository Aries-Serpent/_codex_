#!/usr/bin/env python3
"""Structured wrapper around auto_fix_common_issues.py for campaign workflows."""

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


def run_enhanced_diagnostics(
    repo_root: Path,
    pattern: int | None = None,
    pattern_name: str | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Run detection-only diagnostics and enrich the JSON payload."""

    fixer = CommonIssueFixer(repo_root=repo_root, check_only=True)
    if pattern is not None:
        fixer.run_all_patterns(pattern_num=pattern)
    elif pattern_name:
        fixer.run_all_patterns(pattern_name=pattern_name)
    else:
        fixer.run_all_patterns()

    report = fixer.generate_json_report()
    issues = report.get("issues", [])
    errors = sum(1 for issue in issues if issue.get("severity") == "error")
    warnings = sum(1 for issue in issues if issue.get("severity") == "warning")
    report["generated_at"] = _utc_timestamp()
    report["summary"] = {
        "errors": errors,
        "warnings": warnings,
        "blocking_patterns": sorted(
            {
                issue.get("pattern_name", "unknown")
                for issue in issues
                if issue.get("severity") == "error"
            }
        ),
    }
    report["recommended_command"] = (
        "python scripts/ci/bulk_remediation_orchestrator.py"
        if report.get("auto_fixable", 0) > 0
        else "No blocking auto-fixable issues remain."
    )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main() -> None:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description="Run enhanced CI diagnostics")
    parser.add_argument("--repo-root", default=".", help="Repository root to scan")
    parser.add_argument("--pattern", type=int, default=None, help="Pattern number to scan")
    parser.add_argument(
        "--pattern-name",
        default=None,
        help="Pattern-name substring to scan when --pattern is not supplied",
    )
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    args = parser.parse_args()

    report = run_enhanced_diagnostics(
        repo_root=Path(args.repo_root).resolve(),
        pattern=args.pattern,
        pattern_name=args.pattern_name,
        output_path=Path(args.output).resolve() if args.output else None,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
