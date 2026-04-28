#!/usr/bin/env python3
"""
Collect Git Data

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/collect_git_data.py [options]

    Examples:
    $ python scripts/cognitive/collect_git_data.py --help

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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def collect_git_commits(since_date: str, output_path: str) -> Dict[str, Any]:
    """
    Collect Git commit data for cognitive analysis.

    Args:
        since_date: Date string (e.g., "7 days ago")
        output_path: Path to save JSON output

    Returns:
        Dictionary with commit data and metadata
    """
    try:
        # Get commit history
        cmd = [
            "git", "log",
            f"--since={since_date}",
            "--pretty=format:%H|%an|%ae|%at|%s",
            "--numstat"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        commits = []
        lines = result.stdout.split('\n')

        current_commit = None
        for line in lines:
            if '|' in line and len(line.split('|')) >= 5:
                # New commit entry
                parts = line.split('|')
                if current_commit:
                    commits.append(current_commit)

                current_commit = {
                    "hash": parts[0],
                    "author_name": parts[1],
                    "author_email": parts[2],
                    "timestamp": int(parts[3]),
                    "subject": parts[4],
                    "files_changed": [],
                    "additions": 0,
                    "deletions": 0
                }
            elif current_commit and '\t' in line:
                # File change stats
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        additions = int(parts[0]) if parts[0].isdigit() else 0
                        deletions = int(parts[1]) if parts[1].isdigit() else 0
                        filename = parts[2]

                        current_commit["files_changed"].append({
                            "file": filename,
                            "additions": additions,
                            "deletions": deletions
                        })
                        current_commit["additions"] += additions
                        current_commit["deletions"] += deletions
                    except (ValueError, IndexError):
                        continue

        # Add last commit
        if current_commit:
            commits.append(current_commit)

        # Generate statistics
        total_additions = sum(c["additions"] for c in commits)
        total_deletions = sum(c["deletions"] for c in commits)
        unique_authors = len(set(c["author_email"] for c in commits))

        data = {
            "collection_timestamp": datetime.now().isoformat(),
            "since_date": since_date,
            "total_commits": len(commits),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "unique_authors": unique_authors,
            "commits": commits
        }

        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Collected {len(commits)} commits from {unique_authors} authors")
        print(f"   Additions: {total_additions}, Deletions: {total_deletions}")
        print(f"   Saved to: {output_path}")

        return data

    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        return {"error": str(e), "commits": []}
    except Exception as e:
        print(f"❌ Error collecting Git data: {e}")
        return {"error": str(e), "commits": []}


def main():
    parser = argparse.ArgumentParser(
        description="Collect Git commit data for cognitive brain perception"
    )
    parser.add_argument(
        "--since",
        default="7 days ago",
        help="Collect commits since this date (default: '7 days ago')"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )

    args = parser.parse_args()

    collect_git_commits(args.since, args.output)


if __name__ == "__main__":
    main()
