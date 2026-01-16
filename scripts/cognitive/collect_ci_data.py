#!/usr/bin/env python3
"""
Collect Ci Data

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/collect_ci_data.py [options]
    
    Examples:
    $ python scripts/cognitive/collect_ci_data.py --help

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


"""
Cognitive Brain - CI/CD Data Collector
Part of Perception Layer - collects GitHub Actions workflow run data
"""
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def collect_ci_data(max_runs: int, output_path: str) -> Dict[str, Any]:
    """
    Collect CI/CD workflow run data using GitHub CLI.
    
    Args:
        max_runs: Maximum number of workflow runs to collect
        output_path: Path to save JSON output
    
    Returns:
        Dictionary with CI/CD data and metrics
    """
    try:
        # Get workflow runs
        runs_cmd = [
            "gh", "run", "list",
            "--limit", str(max_runs),
            "--json", "databaseId,name,displayTitle,event,status,conclusion,createdAt,updatedAt,workflowName,headBranch"
        ]
        
        runs_result = subprocess.run(
            runs_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        runs = json.loads(runs_result.stdout)
        
        # Calculate metrics
        total_runs = len(runs)
        successful_runs = sum(1 for r in runs if r.get("conclusion") == "success")
        failed_runs = sum(1 for r in runs if r.get("conclusion") == "failure")
        cancelled_runs = sum(1 for r in runs if r.get("conclusion") == "cancelled")
        in_progress_runs = sum(1 for r in runs if r.get("status") == "in_progress")
        
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Calculate average duration for completed runs
        durations = []
        for run in runs:
            if run.get("createdAt") and run.get("updatedAt") and run.get("conclusion"):
                created = datetime.fromisoformat(run["createdAt"].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(run["updatedAt"].replace('Z', '+00:00'))
                duration_seconds = (updated - created).total_seconds()
                durations.append(duration_seconds)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Group by workflow
        workflow_stats = {}
        for run in runs:
            wf_name = run.get("workflowName", "unknown")
            if wf_name not in workflow_stats:
                workflow_stats[wf_name] = {
                    "total": 0,
                    "success": 0,
                    "failure": 0,
                    "cancelled": 0
                }
            workflow_stats[wf_name]["total"] += 1
            conclusion = run.get("conclusion")
            if conclusion == "success":
                workflow_stats[wf_name]["success"] += 1
            elif conclusion == "failure":
                workflow_stats[wf_name]["failure"] += 1
            elif conclusion == "cancelled":
                workflow_stats[wf_name]["cancelled"] += 1
        
        data = {
            "collection_timestamp": datetime.now().isoformat(),
            "max_runs_requested": max_runs,
            "metrics": {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "cancelled_runs": cancelled_runs,
                "in_progress_runs": in_progress_runs,
                "success_rate_percent": round(success_rate, 2),
                "avg_duration_seconds": round(avg_duration, 2),
                "avg_duration_minutes": round(avg_duration / 60, 2)
            },
            "workflow_statistics": workflow_stats,
            "runs": runs
        }
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Collected {total_runs} CI/CD workflow runs")
        print(f"   Success: {successful_runs}, Failed: {failed_runs}, Cancelled: {cancelled_runs}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Avg duration: {avg_duration/60:.1f} minutes")
        print(f"   Saved to: {output_path}")
        
        return data
        
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI command failed: {e}")
        return {"error": str(e), "runs": []}
    except Exception as e:
        print(f"❌ Error collecting CI/CD data: {e}")
        return {"error": str(e), "runs": []}


def main():
    parser = argparse.ArgumentParser(
        description="Collect CI/CD workflow data for cognitive brain perception"
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=100,
        help="Maximum number of workflow runs to collect (default: 100)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )
    
    args = parser.parse_args()
    
    collect_ci_data(args.max_runs, args.output)


if __name__ == "__main__":
    main()
