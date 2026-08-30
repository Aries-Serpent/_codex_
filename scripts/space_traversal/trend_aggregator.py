#!/usr/bin/env python3
"""
Trend Aggregator

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/space_traversal/trend_aggregator.py [options]

    Examples:
    $ python scripts/space_traversal/trend_aggregator.py --help

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

import logging

logger = logging.getLogger(__name__)

# trend_aggregator.py — Trend aggregation across past audit manifests/reports
#
# Features:
# - Aggregates capability scores across multiple audit runs
# - Supports lookback_days filter for time-based analysis
# - Generates trend reports under audit_artifacts/trends/
# - Deterministic ordering and output
# - CLI entry point for standalone execution
#
# API:
# - aggregate_trends(artifacts_dir, reports_dir, lookback_days, manifest_paths) -> dict
# - CLI: python -m scripts.space_traversal.trend_aggregator --lookback-days 30

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]


def _load_manifest_or_scored(path: Path) -> Optional[dict[str, Any]]:
    """
    Load a manifest or capabilities_scored.json file.

    Returns dict with timestamp and capabilities list.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Extract timestamp
        timestamp = data.get("timestamp") or data.get("generated", 0)
        if isinstance(timestamp, str):
            # Try parsing ISO format
            try:
                dt = datetime.fromisoformat(timestamp.replace("UTC", "").strip())
                timestamp = dt.timestamp()
            except (ValueError, TypeError) as e:
                logger.debug(f"Exception: {e}")
                # Fallback to 0 if parsing fails
                timestamp = 0

        # Extract capabilities
        capabilities = data.get("capabilities", [])

        return {"timestamp": timestamp, "capabilities": capabilities, "source": str(path)}
    except (OSError, json.JSONDecodeError) as e:
        logger.debug(f"Exception: {e}")
        print(f"Failed to load {path}: {e}", file=sys.stderr)
        return None


def _filter_by_lookback(
    runs: list[dict[str, Any]], lookback_days: Optional[int]
) -> list[dict[str, Any]]:
    """
    Filter runs to only include those within lookback_days.

    Args:
        runs: list of run data dictionaries
        lookback_days: Number of days to look back (None = no filter)

    Returns:
        Filtered list of runs
    """
    if lookback_days is None:
        return runs

    cutoff = time.time() - (lookback_days * 86400)
    return [r for r in runs if r["timestamp"] >= cutoff]


def aggregate_trends(
    artifacts_dir: Path,
    reports_dir: Path,
    lookback_days: Optional[int] = None,
    manifest_paths: Optional[list[Path]] = None,
) -> dict[str, Any]:
    """
    Aggregate capability trends across multiple audit runs.

    Searches for:
    1. audit_run_manifest.json files in ROOT and reports_dir
    2. capabilities_scored_*.json files in artifacts_dir
    3. manifest.json files in reports_dir subdirectories
    4. Explicitly provided manifest_paths

    Args:
        artifacts_dir: Directory containing audit artifacts
        reports_dir: Directory containing reports
        lookback_days: Only include runs from last N days (None = all)
        manifest_paths: Optional explicit list of manifest files to include

    Returns:
        Aggregated trend data with:
        - capability_trends: per-capability score history
        - run_count: number of runs analyzed
        - time_range: earliest and latest timestamps
        - summary_stats: aggregate statistics
    """
    runs = []

    # Collect all potential manifest/scored files
    paths_to_check: list[Path] = []

    # 1. Root manifest
    root_manifest = ROOT / "audit_run_manifest.json"
    if root_manifest.exists():
        paths_to_check.append(root_manifest)

    # 2. Scored capabilities in artifacts_dir
    if artifacts_dir.exists():
        paths_to_check.extend(artifacts_dir.glob("capabilities_scored*.json"))

    # 3. Reports directory manifests
    if reports_dir.exists():
        paths_to_check.extend(reports_dir.glob("**/audit_run_manifest.json"))
        paths_to_check.extend(reports_dir.glob("**/manifest.json"))
        paths_to_check.extend(reports_dir.glob("capabilities_scored*.json"))

    # 4. Explicit paths
    if manifest_paths:
        paths_to_check.extend(manifest_paths)

    # Load all files
    for path in sorted(set(paths_to_check), key=str):
        run_data = _load_manifest_or_scored(path)
        if run_data and run_data["capabilities"]:
            runs.append(run_data)

    # Filter by lookback
    runs = _filter_by_lookback(runs, lookback_days)

    # Sort by timestamp
    runs.sort(key=lambda r: r["timestamp"])

    if not runs:
        return {
            "capability_trends": {},
            "run_count": 0,
            "time_range": None,
            "summary_stats": {},
            "error": "No audit runs found",
        }

    # Aggregate trends per capability
    capability_trends = defaultdict(list)
    for run in runs:
        run_ts = run["timestamp"]
        for cap in run["capabilities"]:
            cap_id = cap.get("id")
            score = cap.get("score")
            if cap_id and score is not None:
                capability_trends[cap_id].append(
                    {"timestamp": run_ts, "score": round(float(score), 6), "source": run["source"]}
                )

    # Calculate summary stats
    all_scores = []
    for _cap_id, trend_data in capability_trends.items():
        scores = [d["score"] for d in trend_data]
        all_scores.extend(scores)

    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

    # Calculate trends (improvement/decline)
    trending_up = []
    trending_down = []
    stable = []

    for _cap_id, trend_data in capability_trends.items():
        if len(trend_data) >= 2:
            first_score = trend_data[0]["score"]
            last_score = trend_data[-1]["score"]
            delta = last_score - first_score

            if abs(delta) < 0.01:
                stable.append(_cap_id)
            elif delta > 0:
                trending_up.append((_cap_id, delta))
            else:
                trending_down.append((_cap_id, delta))

    # Sort trending lists
    trending_up.sort(key=lambda x: x[1], reverse=True)
    trending_down.sort(key=lambda x: x[1])

    return {
        "capability_trends": dict(capability_trends),
        "run_count": len(runs),
        "time_range": {
            "earliest": runs[0]["timestamp"],
            "latest": runs[-1]["timestamp"],
            "earliest_iso": datetime.fromtimestamp(runs[0]["timestamp"]).isoformat(),
            "latest_iso": datetime.fromtimestamp(runs[-1]["timestamp"]).isoformat(),
        },
        "summary_stats": {
            "avg_score": round(avg_score, 6),
            "capabilities_tracked": len(capability_trends),
            "trending_up": [{"id": cid, "delta": round(delta, 6)} for cid, delta in trending_up],
            "trending_down": [
                {"id": cid, "delta": round(delta, 6)} for cid, delta in trending_down
            ],
            "stable": stable,
        },
    }



def generate_trend_report(trend_data: dict[str, Any], output_path: Path) -> None:
    """
    Generate a formatted trend report file.

    Args:
        trend_data: Output from aggregate_trends()
        output_path: Path to write report
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate markdown report
    lines = [
        "# Capability Audit Trend Report",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Summary",
        "",
        f"- **Runs Analyzed**: {trend_data['run_count']}",
        f"- **Capabilities Tracked**: {trend_data['summary_stats']['capabilities_tracked']}",
        f"- **Average Score**: {trend_data['summary_stats']['avg_score']:.4f}",
        "",
    ]

    if trend_data.get("time_range"):
        tr = trend_data["time_range"]
        lines.extend([f"- **Time Range**: {tr['earliest_iso']} to {tr['latest_iso']}", ""])

    # Trending up
    stats = trend_data["summary_stats"]
    if stats["trending_up"]:
        lines.extend(
            ["## Improving Capabilities", "", "| Capability | Delta |", "|------------|-------|"]
        )
        for item in stats["trending_up"][:10]:  # Top 10
            lines.append(f"| {item['id']} | +{item['delta']:.4f} |")
        lines.append("")

    # Trending down
    if stats["trending_down"]:
        lines.extend(
            ["## Declining Capabilities", "", "| Capability | Delta |", "|------------|-------|"]
        )
        for item in stats["trending_down"][:10]:  # Top 10
            lines.append(f"| {item['id']} | {item['delta']:.4f} |")
        lines.append("")

    # Stable
    if stats["stable"]:
        lines.extend(["## Stable Capabilities", "", f"Count: {len(stats['stable'])}", ""])

    report_content = "\n".join(lines)
    output_path.write_text(report_content, encoding="utf-8")

    # Also write JSON for programmatic access
    json_path = output_path.with_suffix(".json")
    json_path.write_text(json.dumps(trend_data, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Trend report written to: {output_path}")
    print(f"Trend data (JSON) written to: {json_path}")


def main():
    """CLI entry point for trend aggregation."""
    parser = argparse.ArgumentParser(
        description="Aggregate capability audit trends across multiple runs"
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("audit_artifacts"),
        help="Directory containing audit artifacts (default: audit_artifacts)",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path(".codex/reports"),
        help="Directory containing reports (default: .codex/reports)",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=None,
        help="Only analyze runs from last N days (default: all)",
    )
    parser.add_argument(
        "--manifest-paths", nargs="*", type=Path, help="Additional manifest files to include"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for trend report (default: audit_artifacts/trends/trend_report.md)",
    )

    args = parser.parse_args()

    # Determine output path
    if args.output is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        args.output = args.artifacts_dir / "trends" / f"trend_report_{timestamp}.md"

    # Aggregate trends
    print("Aggregating trends from:")
    print(f"  Artifacts: {args.artifacts_dir}")
    print(f"  Reports: {args.reports_dir}")
    if args.lookback_days:
        print(f"  Lookback: {args.lookback_days} days")

    trend_data = aggregate_trends(
        args.artifacts_dir, args.reports_dir, args.lookback_days, args.manifest_paths
    )

    if trend_data.get("error"):
        print(f"Error: {trend_data['error']}", file=sys.stderr)
        sys.exit(1)

    # Generate report
    generate_trend_report(trend_data, args.output)

    print("\nSummary:")
    print(f"  Runs analyzed: {trend_data['run_count']}")
    print(f"  Capabilities tracked: {trend_data['summary_stats']['capabilities_tracked']}")
    print(f"  Average score: {trend_data['summary_stats']['avg_score']:.4f}")


if __name__ == "__main__":
    main()
