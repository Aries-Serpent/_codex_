#!/usr/bin/env python3
"""
Phase 8.1 Metrics Collector
Collects CI/CD health metrics from GitHub Actions and generates reports.

Version: 1.0.0-final
Author: Phase 8.1 Monitoring System
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)


class MetricsCollector:
    """Collects CI/CD metrics from GitHub Actions API."""

    def __init__(self, owner: str, repo: str, token: str):
        """Initialize metrics collector.

        Args:
            owner: Repository owner
            repo: Repository name
            token: GitHub API token
        """
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "owner": owner,
            "repo": repo,
            "workflows": {},
            "aggregated": {},
        }

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get list of all workflows in repository.

        Returns:
            List of workflow dictionaries
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("workflows", [])
        except requests.RequestException as e:
            print(f"ERROR: Failed to get workflows: {e}")
            return []

    def get_workflow_runs(
        self, workflow_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent runs for a workflow.

        Args:
            workflow_id: Workflow ID or filename
            limit: Number of runs to fetch

        Returns:
            List of workflow run dictionaries
        """
        url = (
            f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/"
            f"workflows/{workflow_id}/runs"
        )
        params = {"per_page": min(limit, 100)}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("workflow_runs", [])
        except requests.RequestException as e:
            print(f"ERROR: Failed to get runs for {workflow_id}: {e}")
            return []

    def calculate_workflow_metrics(
        self, workflow: Dict[str, Any], runs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for a single workflow.

        Args:
            workflow: Workflow definition
            runs: List of recent runs

        Returns:
            Dictionary with calculated metrics
        """
        if not runs:
            return {
                "workflow_id": workflow["id"],
                "workflow_name": workflow["name"],
                "status": "no_data",
                "total_runs": 0,
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "avg_duration_seconds": 0,
                "last_run": None,
            }

        # Count statuses
        status_counts = {}
        total_duration = 0
        completed_count = 0

        for run in runs:
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "unknown")

            # Aggregate key
            key = f"{status}:{conclusion}"
            status_counts[key] = status_counts.get(key, 0) + 1

            # Calculate duration if available
            if run.get("run_number"):
                created = datetime.fromisoformat(
                    run["created_at"].replace("Z", "+00:00")
                )
                updated = datetime.fromisoformat(
                    run["updated_at"].replace("Z", "+00:00")
                )
                duration = (updated - created).total_seconds()
                if duration > 0:
                    total_duration += duration
                    completed_count += 1

        # Calculate rates
        success_count = status_counts.get("completed:success", 0)
        failure_count = status_counts.get("completed:failure", 0)
        total = len(runs)

        success_rate = (success_count / total * 100) if total > 0 else 0.0
        failure_rate = (failure_count / total * 100) if total > 0 else 0.0
        avg_duration = (total_duration / completed_count) if completed_count > 0 else 0

        # Determine current status
        if runs[0]["conclusion"] == "success":
            status = "passing"
        elif runs[0]["conclusion"] == "failure":
            status = "failing"
        elif runs[0]["status"] == "in_progress":
            status = "in_progress"
        else:
            status = "unknown"

        return {
            "workflow_id": workflow["id"],
            "workflow_name": workflow["name"],
            "status": status,
            "total_runs": total,
            "success_rate": round(success_rate, 2),
            "failure_rate": round(failure_rate, 2),
            "avg_duration_seconds": int(avg_duration),
            "last_run": runs[0].get("created_at"),
            "status_breakdown": status_counts,
        }

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect all metrics from GitHub Actions.

        Returns:
            Complete metrics dictionary
        """
        print(f"Collecting metrics for {self.owner}/{self.repo}...")

        workflows = self.get_workflows()
        print(f"Found {len(workflows)} workflows")

        total_success = 0
        total_failure = 0
        total_runs = 0
        total_duration = 0
        completed_workflows = 0

        for workflow in workflows:
            workflow_id = workflow["id"]
            print(f"  Processing {workflow['name']}...", end=" ")

            runs = self.get_workflow_runs(workflow_id)
            metrics = self.calculate_workflow_metrics(workflow, runs)

            self.metrics["workflows"][workflow["name"]] = metrics

            # Aggregate
            total_runs += metrics["total_runs"]
            total_success += int(
                metrics["success_rate"] / 100 * metrics["total_runs"]
            )
            total_failure += int(
                metrics["failure_rate"] / 100 * metrics["total_runs"]
            )
            if metrics["avg_duration_seconds"] > 0:
                total_duration += metrics["avg_duration_seconds"]
                completed_workflows += 1

            status_icon = (
                "✓" if metrics["status"] == "passing" else "✗"
                if metrics["status"] == "failing"
                else "●"
            )
            print(f"{status_icon} ({metrics['total_runs']} runs)")

        # Calculate aggregated metrics
        if total_runs > 0:
            aggregated_success_rate = total_success / total_runs * 100
            aggregated_failure_rate = total_failure / total_runs * 100
        else:
            aggregated_success_rate = 0.0
            aggregated_failure_rate = 0.0

        avg_duration = (
            (total_duration / completed_workflows) if completed_workflows > 0 else 0
        )

        self.metrics["aggregated"] = {
            "total_workflows": len(workflows),
            "total_runs_24h": total_runs,
            "aggregated_success_rate": round(aggregated_success_rate, 2),
            "aggregated_failure_rate": round(aggregated_failure_rate, 2),
            "avg_workflow_duration_seconds": int(avg_duration),
            "workflows_passing": sum(
                1
                for m in self.metrics["workflows"].values()
                if m["status"] == "passing"
            ),
            "workflows_failing": sum(
                1
                for m in self.metrics["workflows"].values()
                if m["status"] == "failing"
            ),
            "workflows_in_progress": sum(
                1
                for m in self.metrics["workflows"].values()
                if m["status"] == "in_progress"
            ),
        }

        return self.metrics

    def save_metrics(self, output_path: Optional[str] = None) -> str:
        """Save metrics to JSON file.

        Args:
            output_path: Output file path (default: .codex/metrics/latest.json)

        Returns:
            Path to saved file
        """
        if output_path is None:
            output_path = ".codex/metrics/latest.json"

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.metrics, f, indent=2)

        print(f"Metrics saved to {output_path}")
        return output_path

    def print_summary(self) -> None:
        """Print metrics summary to console."""
        agg = self.metrics.get("aggregated", {})

        print("\n" + "=" * 60)
        print("CI/CD METRICS SUMMARY")
        print("=" * 60)
        print(f"Timestamp: {self.metrics['timestamp']}")
        print(f"Repository: {self.owner}/{self.repo}")
        print()
        print("AGGREGATED METRICS:")
        print(f"  Total Workflows: {agg.get('total_workflows', 0)}")
        print(f"  Total Runs (24h): {agg.get('total_runs_24h', 0)}")
        print(f"  Success Rate: {agg.get('aggregated_success_rate', 0):.2f}%")
        print(f"  Failure Rate: {agg.get('aggregated_failure_rate', 0):.2f}%")
        print(f"  Avg Duration: {agg.get('avg_workflow_duration_seconds', 0)}s")
        print()
        print("WORKFLOW DISTRIBUTION:")
        print(f"  Passing: {agg.get('workflows_passing', 0)}")
        print(f"  Failing: {agg.get('workflows_failing', 0)}")
        print(f"  In Progress: {agg.get('workflows_in_progress', 0)}")
        print("=" * 60 + "\n")


def main() -> int:
    """Main entry point."""
    # Get credentials from environment
    token = os.getenv("GITHUB_TOKEN") or os.getenv("COPILOT_MASTER_KEY")
    owner = os.getenv("GITHUB_REPOSITORY_OWNER", "Aries-Serpent")
    repo = os.getenv("GITHUB_REPOSITORY", "Aries-Serpent/_codex_").split("/")[-1]

    if not token:
        print("ERROR: GITHUB_TOKEN or COPILOT_MASTER_KEY environment variable required")
        return 1

    # Create collector
    collector = MetricsCollector(owner, repo, token)

    # Collect metrics
    metrics = collector.collect_metrics()

    # Save metrics
    collector.save_metrics()

    # Print summary
    collector.print_summary()

    print(f"✓ Metrics collection completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
