#!/usr/bin/env python3
"""
phase_8_3_benchmark_collector.py — Collect GitHub Actions performance metrics.

Collects metrics for:
- Workflow execution times
- Job execution times
- API response times
- Artifact processing times
- Cache hit rates

Usage:
    python scripts/ci/phase_8_3_benchmark_collector.py
    python scripts/ci/phase_8_3_benchmark_collector.py --hours 24
    python scripts/ci/phase_8_3_benchmark_collector.py --workflow "CI" --export-json metrics.json
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics."""
    workflow_name: str
    run_id: int
    status: str
    created_at: str
    updated_at: str
    duration_ms: int
    conclusion: str
    actor: str
    branch: str
    commit_sha: str


@dataclass
class JobMetrics:
    """Job-level execution metrics."""
    workflow_name: str
    run_id: int
    job_name: str
    status: str
    started_at: str
    completed_at: str
    duration_ms: int
    conclusion: str
    runner_name: str


@dataclass
class PercentileMetrics:
    """Percentile calculations."""
    count: int = 0
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    median_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    stdev_ms: float = 0.0

    @classmethod
    def from_samples(cls, samples: list[float]) -> PercentileMetrics:
        """Calculate percentiles from samples."""
        if not samples:
            return cls()

        sorted_samples = sorted(samples)
        count = len(sorted_samples)

        result = cls(
            count=count,
            min_ms=round(sorted_samples[0], 2),
            max_ms=round(sorted_samples[-1], 2),
            mean_ms=round(statistics.mean(sorted_samples), 2),
            median_ms=round(statistics.median(sorted_samples), 2),
        )

        if count > 1:
            result.stdev_ms = round(statistics.stdev(sorted_samples), 2)

        # Calculate percentiles
        result.p50_ms = round(sorted_samples[int(count * 0.50)], 2)
        result.p95_ms = round(sorted_samples[int(count * 0.95)], 2)
        result.p99_ms = round(sorted_samples[int(count * 0.99)], 2)

        return result


class GitHubActionsMetricsCollector:
    """Collect performance metrics from GitHub Actions."""

    def __init__(self, owner: str, repo: str, token: str | None = None):
        """Initialize collector."""
        self.owner = owner
        self.repo = repo
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        self.base_url = "https://api.github.com"

    def get_workflows(self, hours: int = 24) -> dict[str, Any]:
        """Get workflow runs from the last N hours."""
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs"
        params = {
            "created": f">={since}",
            "per_page": 100,
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflows: {e}")
            return {"workflow_runs": []}

    def get_jobs(self, run_id: int) -> dict[str, Any]:
        """Get jobs for a specific workflow run."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/jobs"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs for run {run_id}: {e}")
            return {"jobs": []}

    def collect_metrics(
        self, hours: int = 24, workflow_filter: str | None = None
    ) -> dict[str, Any]:
        """Collect all metrics."""
        print(f"Collecting GitHub Actions metrics for {self.owner}/{self.repo}...")
        print(f"Looking back: {hours} hours")

        workflows = self.get_workflows(hours)
        workflow_runs = workflows.get("workflow_runs", [])

        if workflow_filter:
            workflow_runs = [
                w for w in workflow_runs
                if workflow_filter.lower() in w.get("name", "").lower()
            ]

        print(f"Found {len(workflow_runs)} workflow runs")

        # Collect workflow metrics
        workflow_durations = {}
        job_durations_by_workflow = {}

        for run in workflow_runs:
            workflow_name = run.get("name", "Unknown")
            run_id = run.get("id")
            created_at = run.get("created_at", "")
            updated_at = run.get("updated_at", "")

            # Calculate duration
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                duration_ms = int((updated - created).total_seconds() * 1000)
            except (ValueError, TypeError):
                duration_ms = 0

            # Track workflow duration
            if workflow_name not in workflow_durations:
                workflow_durations[workflow_name] = []
            workflow_durations[workflow_name].append(duration_ms)

            # Collect job metrics
            jobs_data = self.get_jobs(run_id)
            jobs = jobs_data.get("jobs", [])

            if workflow_name not in job_durations_by_workflow:
                job_durations_by_workflow[workflow_name] = []

            for job in jobs:
                job_name = job.get("name", "Unknown")
                started_at = job.get("started_at", "")
                completed_at = job.get("completed_at", "")

                # Calculate job duration
                try:
                    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    completed = datetime.fromisoformat(
                        completed_at.replace("Z", "+00:00")
                    )
                    job_duration_ms = int((completed - started).total_seconds() * 1000)
                except (ValueError, TypeError):
                    job_duration_ms = 0

                job_durations_by_workflow[workflow_name].append(job_duration_ms)

        # Calculate percentiles
        workflow_stats = {}
        for workflow_name, durations in workflow_durations.items():
            workflow_stats[workflow_name] = asdict(
                PercentileMetrics.from_samples(durations)
            )

        job_stats = {}
        for workflow_name, durations in job_durations_by_workflow.items():
            job_stats[workflow_name] = asdict(
                PercentileMetrics.from_samples(durations)
            )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hours_lookback": hours,
            "workflow_count": len(workflow_runs),
            "workflow_execution_time": workflow_stats,
            "job_execution_time": job_stats,
            "total_runs_analyzed": len(workflow_runs),
        }

    def export_json(self, metrics: dict[str, Any], filepath: Path) -> None:
        """Export metrics to JSON."""
        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"Metrics exported to: {filepath}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Collect GitHub Actions performance metrics"
    )
    parser.add_argument(
        "--owner",
        default="Aries-Serpent",
        help="Repository owner (default: Aries-Serpent)",
    )
    parser.add_argument(
        "--repo",
        default="_codex_",
        help="Repository name (default: _codex_)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to look back (default: 24)",
    )
    parser.add_argument(
        "--workflow",
        help="Filter by workflow name",
    )
    parser.add_argument(
        "--export-json",
        help="Export metrics to JSON file",
    )

    args = parser.parse_args()

    # Collect metrics
    collector = GitHubActionsMetricsCollector(args.owner, args.repo)
    metrics = collector.collect_metrics(hours=args.hours, workflow_filter=args.workflow)

    # Print summary
    print("\n" + "=" * 80)
    print("METRICS SUMMARY")
    print("=" * 80)
    print(f"Timestamp: {metrics['timestamp']}")
    print(f"Lookback: {metrics['hours_lookback']} hours")
    print(f"Total runs analyzed: {metrics['total_runs_analyzed']}")
    print("\nWorkflow Execution Times (ms):")
    for workflow, stats in metrics["workflow_execution_time"].items():
        print(f"  {workflow}:")
        print(f"    Mean: {stats['mean_ms']:.2f}ms")
        print(f"    P95:  {stats['p95_ms']:.2f}ms")
        print(f"    P99:  {stats['p99_ms']:.2f}ms")

    # Export if requested
    if args.export_json:
        export_path = Path(args.export_json)
        collector.export_json(metrics, export_path)

    print("\n✅ Metrics collection complete")


if __name__ == "__main__":
    main()
