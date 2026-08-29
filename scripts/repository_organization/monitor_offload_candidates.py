#!/usr/bin/env python3
"""
Repository Offload Candidates Monitoring Script

Purpose:
    Scan repository for files meeting offload criteria and generate report

Usage:
    python scripts/repository_organization/monitor_offload_candidates.py [options]

    Examples:
    $ python scripts/repository_organization/monitor_offload_candidates.py --help
    $ python scripts/repository_organization/monitor_offload_candidates.py --output .codex/repository_health/offload_candidates.json

Arguments:
    --repo-root: Repository root directory (default: current directory)
    --output: Output JSON file path
    --log-actions: Log findings to action log (default: True)

Exit Codes:
    0: Success
    1: Error

Author: QA Walkthrough Agent
Last Updated: 2026-01-26
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Offload criteria configuration
CRITERIA = {
    "temp_files_age_days": 90,
    "deprecated_reports_age_days": 180,
    "large_file_size_mb": 1.0,
    "unused_file_age_days": 180,
}

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".nox",
    ".tox",
    "dist",
    "build",
    ".eggs",
    "htmlcov",
    "site",
    "misc/repo-owner-review",  # Already offloaded
}

# File patterns to consider for offload
# Note: More specific patterns (paths) should be checked before generic patterns (extensions)
OFFLOAD_PATTERNS = {
    "temp": ["temp/", "tmp/", "output/", ".tmp"],
    "artifacts": ["artifacts/gates/", "artifacts/validate_"],
    "reports": [".codex/reports/", ".codex/archive/"],
    "logs": ["*.log", "logs/"],
    "coverage": ["coverage_", "*.coverage", "htmlcov/"],
}

LOCK_FILE_NAMES = {
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
}

# Essential repository files in the root that should never be offloaded
ESSENTIAL_ROOT_FILES = {
    "CHANGELOG.md",
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
}


def _exclude_from_large_file_check(rel_path: Path) -> bool:
    """Exclude essential lock/docs files from large-file offload heuristics.

    Lock files (e.g. `uv.lock`) are required for deterministic dependency
    resolution, and documentation under `docs/` is intentionally maintained in-repo.
    Essential root markdown files (CHANGELOG.md, README.md, etc.) are core
    repository documents and should never be flagged as offload candidates.
    These should never be suggested as offload candidates purely due to file size.
    """
    rel_str = str(rel_path)
    return (
        rel_path.name in LOCK_FILE_NAMES
        or rel_path.suffix == ".lock"
        or rel_str.startswith("docs/")
        or rel_path.name in ESSENTIAL_ROOT_FILES
        or (rel_path.parent == Path(".") and rel_path.name in ESSENTIAL_ROOT_FILES)
    )


def get_file_age_days(file_path: Path) -> int:
    """Get file age in days based on modification time."""
    try:
        mtime = file_path.stat().st_mtime
        age_seconds = datetime.now(timezone.utc).timestamp() - mtime
        return int(age_seconds / 86400)  # Convert to days
    except (OSError, ValueError):
        return 0


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except (OSError, ValueError):
        return 0.0


def matches_pattern(file_path: Path, patterns: list[str]) -> bool:
    """Check if file matches any of the given patterns."""
    file_str = str(file_path)
    for pattern in patterns:
        if pattern.endswith("/"):
            # Directory pattern
            if pattern in file_str:
                return True
        elif pattern.startswith("*."):
            # Extension pattern
            if file_path.suffix == pattern[1:]:
                return True
        elif pattern in file_str:
            # Substring pattern
            return True
    return False


def should_exclude_dir(dir_path: Path, repo_root: Path) -> bool:
    """Check if directory should be excluded from scanning."""
    rel_path = str(dir_path.relative_to(repo_root))
    return any(exclude in rel_path or dir_path.name in EXCLUDE_DIRS for exclude in EXCLUDE_DIRS)


def categorize_file(file_path: Path, repo_root: Path) -> str | None:
    """Categorize file based on offload patterns."""
    rel_path = file_path.relative_to(repo_root)

    for category, patterns in OFFLOAD_PATTERNS.items():
        if matches_pattern(rel_path, patterns):
            return category

    return None


def scan_repository(repo_root: Path) -> dict[str, Any]:
    """Scan repository for offload candidates."""
    candidates = {
        "metadata": {
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "repo_root": str(repo_root),
            "criteria": CRITERIA,
        },
        "summary": {
            "total_candidates": 0,
            "by_reason": {},
            "by_category": {},
            "total_size_mb": 0.0,
        },
        "candidates": [],
    }

    for root, dirs, files in os.walk(repo_root):
        root_path = Path(root)

        # Filter out excluded directories
        dirs[:] = [
            d for d in dirs
            if not should_exclude_dir(root_path / d, repo_root)
        ]

        for filename in files:
            file_path = root_path / filename
            rel_path = file_path.relative_to(repo_root)

            # Skip if file doesn't exist or can't be accessed
            if not file_path.exists():
                continue

            age_days = get_file_age_days(file_path)
            size_mb = get_file_size_mb(file_path)
            category = categorize_file(file_path, repo_root)
            reasons = []

            # Check criteria
            if category == "temp" and age_days > CRITERIA["temp_files_age_days"]:
                reasons.append(f"temp_file_age_{age_days}d")

            if category == "reports" and age_days > CRITERIA["deprecated_reports_age_days"]:
                reasons.append(f"deprecated_report_age_{age_days}d")

            if (
                size_mb > CRITERIA["large_file_size_mb"]
                and not _exclude_from_large_file_check(rel_path)
            ):
                reasons.append(f"large_file_{size_mb:.2f}mb")

            if age_days > CRITERIA["unused_file_age_days"] and category:
                reasons.append(f"unused_{age_days}d")

            # Add candidate if it meets any criteria
            if reasons:
                candidate = {
                    "path": str(rel_path),
                    "category": category or "unknown",
                    "age_days": age_days,
                    "size_mb": round(size_mb, 2),
                    "reasons": reasons,
                    "recommendation": _get_recommendation(category, age_days, size_mb),
                }

                candidates["candidates"].append(candidate)
                candidates["summary"]["total_candidates"] += 1
                candidates["summary"]["total_size_mb"] += size_mb

                # Update by_reason counts
                for reason in reasons:
                    reason_key = reason.split("_")[0]
                    candidates["summary"]["by_reason"][reason_key] = (
                        candidates["summary"]["by_reason"].get(reason_key, 0) + 1
                    )

                # Update by_category counts
                candidates["summary"]["by_category"][candidate["category"]] = (
                    candidates["summary"]["by_category"].get(candidate["category"], 0) + 1
                )

    # Round summary total size
    candidates["summary"]["total_size_mb"] = round(
        candidates["summary"]["total_size_mb"], 2
    )

    return candidates


def _get_recommendation(category: str | None, age_days: int, size_mb: float) -> str:
    """Generate offload recommendation based on file characteristics."""
    if category == "temp" and age_days > 90:
        return "offload_to_temp-outputs"
    if category == "reports" and age_days > 180:
        return "offload_to_deprecated-reports"
    if category == "logs" and age_days > 180:
        return "offload_to_historical-logs"
    if category == "coverage" and age_days > 90:
        return "offload_to_historical-coverage"
    if category == "artifacts" and age_days > 180:
        return "offload_to_historical-artifacts"
    if size_mb > 5.0:
        return "compress_or_offload"
    return "review_manually"


def log_to_action_log(
    candidates_summary: dict[str, Any],
    repo_root: Path,
) -> None:
    """Log scan findings to action log."""
    action_log_path = repo_root / ".codex" / "action_log.ndjson"

    action_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "repository-organization-monitor",
        "action": "scan_offload_candidates",
        "category": "repository_health",
        "details": {
            "total_candidates": candidates_summary["total_candidates"],
            "total_size_mb": candidates_summary["total_size_mb"],
            "by_reason": candidates_summary["by_reason"],
            "by_category": candidates_summary["by_category"],
        },
        "outcome": "success",
        "impact": f"Identified {candidates_summary['total_candidates']} offload {'candidate' if candidates_summary['total_candidates'] == 1 else 'candidates'} (~{candidates_summary['total_size_mb']}MB)",
    }

    try:
        with open(action_log_path, "a") as f:
            f.write(json.dumps(action_entry, separators=(",", ":")) + "\n")
        print(f"✅ Logged to {action_log_path}")
    except Exception as e:
        print(f"⚠️ Failed to log to action log: {e}", file=sys.stderr)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scan repository for offload candidates"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/repository_health/offload_candidates.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--log-actions",
        action="store_true",
        default=True,
        help="Log findings to action log (default: True)",
    )
    parser.add_argument(
        "--no-log-actions",
        action="store_false",
        dest="log_actions",
        help="Do not log findings to action log",
    )

    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if not repo_root.exists():
        print(f"❌ Repository root not found: {repo_root}", file=sys.stderr)
        return 1

    print(f"🔍 Scanning repository: {repo_root}")
    print(f"📊 Criteria: {CRITERIA}")
    print()

    # Scan repository
    candidates = scan_repository(repo_root)

    # Print summary
    summary = candidates["summary"]
    print("📈 Scan Results:")
    print(f"  Total candidates: {summary['total_candidates']}")
    print(f"  Total size: {summary['total_size_mb']:.2f} MB")
    print(f"  By reason: {summary['by_reason']}")
    print(f"  By category: {summary['by_category']}")
    print()

    # Save to output file
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(candidates, f, indent=2)
    print(f"✅ Saved report to: {args.output}")

    # Log to action log
    if args.log_actions:
        log_to_action_log(summary, repo_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
