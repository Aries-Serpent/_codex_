#!/usr/bin/env python3
"""
Collect Pr Metrics

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/collect_pr_metrics.py [options]

    Examples:
    $ python scripts/cognitive/collect_pr_metrics.py --help

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


import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def collect_pr_metrics(lookback_days: int, output_path: str) -> dict[str, Any]:
    """
    Collect Pull Request metrics using GitHub CLI.

    Args:
        lookback_days: Number of days to look back
        output_path: Path to save JSON output

    Returns:
        Dictionary with PR data and metrics
    """
    try:
        # Get repository info
        repo_cmd = ["gh", "repo", "view", "--json", "nameWithOwner"]
        repo_result = subprocess.run(
            repo_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        repo_data = json.loads(repo_result.stdout)
        repo_name = repo_data.get("nameWithOwner", "unknown")

        # Collect recent PRs
        pr_cmd = [
            "gh", "pr", "list",
            "--state", "all",
            "--limit", "100",
            "--json", "number,title,state,createdAt,mergedAt,closedAt,additions,deletions,author"
        ]

        pr_result = subprocess.run(
            pr_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        prs = json.loads(pr_result.stdout)

        # Filter by lookback period
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        filtered_prs = []

        for pr in prs:
            created_at = datetime.fromisoformat(pr["createdAt"].replace('Z', '+00:00'))
            if created_at >= cutoff_date:
                filtered_prs.append(pr)

        # Calculate metrics
        total_prs = len(filtered_prs)
        merged_prs = sum(1 for pr in filtered_prs if pr.get("mergedAt"))
        closed_prs = sum(1 for pr in filtered_prs if pr.get("closedAt") and not pr.get("mergedAt"))
        open_prs = sum(1 for pr in filtered_prs if pr["state"] == "OPEN")

        total_additions = sum(pr.get("additions", 0) for pr in filtered_prs)
        total_deletions = sum(pr.get("deletions", 0) for pr in filtered_prs)

        unique_authors = len(set(pr["author"]["login"] for pr in filtered_prs if pr.get("author")))

        # Calculate average time to merge for merged PRs
        merge_times = []
        for pr in filtered_prs:
            if pr.get("mergedAt"):
                created = datetime.fromisoformat(pr["createdAt"].replace('Z', '+00:00'))
                merged = datetime.fromisoformat(pr["mergedAt"].replace('Z', '+00:00'))
                merge_times.append((merged - created).total_seconds() / 3600)  # hours

        avg_merge_time = sum(merge_times) / len(merge_times) if merge_times else 0

        data = {
            "collection_timestamp": datetime.now().isoformat(),
            "repository": repo_name,
            "lookback_days": lookback_days,
            "metrics": {
                "total_prs": total_prs,
                "merged_prs": merged_prs,
                "closed_prs": closed_prs,
                "open_prs": open_prs,
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "unique_authors": unique_authors,
                "avg_merge_time_hours": round(avg_merge_time, 2)
            },
            "pull_requests": filtered_prs
        }

        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Collected {total_prs} PRs from last {lookback_days} days")
        print(f"   Merged: {merged_prs}, Closed: {closed_prs}, Open: {open_prs}")
        print(f"   Unique authors: {unique_authors}")
        print(f"   Avg merge time: {avg_merge_time:.1f} hours")
        print(f"   Saved to: {output_path}")

        return data

    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI command failed: {e}")
        print("   Make sure GITHUB_TOKEN is set and gh CLI is authenticated")
        return {"error": str(e), "pull_requests": []}
    except Exception as e:
        print(f"❌ Error collecting PR metrics: {e}")
        return {"error": str(e), "pull_requests": []}


def main():
    parser = argparse.ArgumentParser(
        description="Collect PR metrics for cognitive brain perception"
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )

    args = parser.parse_args()

    collect_pr_metrics(args.lookback_days, args.output)


if __name__ == "__main__":
    main()
