#!/usr/bin/env python3
"""
Workflow Health Collector - Phase 5 Continuous Monitoring

Collects metrics from GitHub Actions API and stores in JSON format.
Runs daily at 02:00 UTC via .github/workflows/workflow-health-update.yml

Usage:
    python scripts/ci/workflow_health_collector.py --days 30 --output .codex/workflow_health_snapshot.json
    python scripts/ci/workflow_health_collector.py --days 7 --workflow test-comprehensive.yml
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowMetrics:
    """Metrics for a single workflow"""
    workflow_name: str
    workflow_path: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    cancelled_runs: int
    success_rate: float
    average_runtime_seconds: int
    p95_runtime_seconds: int
    cancellation_rate: float
    flakiness_score: float
    last_run_status: str
    last_run_timestamp: str
    last_run_duration_seconds: int
    trend: str  # "improving", "degrading", "stable"
    critical_alerts: int
    high_alerts: int


class WorkflowHealthCollector:
    """Collects workflow health metrics from GitHub Actions"""

    def __init__(self):
        self.repo = os.getenv("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.gh_cli_available = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if gh CLI is available"""
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def get_workflows(self) -> List[Dict]:
        """Get all workflows in the repository"""
        logger.info(f"Fetching workflows from {self.repo}...")
        
        if not self.gh_cli_available:
            logger.error("gh CLI not available")
            return []

        try:
            result = subprocess.run(
                ["gh", "workflow", "list", "-R", self.repo, "--json", "name,path,id"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to fetch workflows: {result.stderr}")
                return []

            workflows = json.loads(result.stdout)
            logger.info(f"Found {len(workflows)} workflows")
            return workflows
        except Exception as e:
            logger.error(f"Error fetching workflows: {e}")
            return []

    def get_workflow_runs(self, workflow_id: str, days: int = 30) -> List[Dict]:
        """Get recent runs for a workflow"""
        since = datetime.utcnow() - timedelta(days=days)
        since_str = since.isoformat() + "Z"
        
        try:
            result = subprocess.run(
                [
                    "gh", "run", "list",
                    "-R", self.repo,
                    "-w", workflow_id,
                    "--created", f">{since_str}",
                    "--json", "status,conclusion,durationMinutes,createdAt",
                    "--limit", "500"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Failed to fetch runs for workflow {workflow_id}")
                return []

            return json.loads(result.stdout) if result.stdout else []
        except Exception as e:
            logger.error(f"Error fetching runs for {workflow_id}: {e}")
            return []

    def calculate_metrics(self, workflow_id: str, workflow_name: str, workflow_path: str, days: int = 30) -> Optional[WorkflowMetrics]:
        """Calculate metrics for a workflow"""
        runs = self.get_workflow_runs(workflow_id, days)
        
        if not runs:
            logger.warning(f"No runs found for {workflow_name}")
            return None

        total_runs = len(runs)
        successful_runs = sum(1 for r in runs if r.get("conclusion") == "success")
        failed_runs = sum(1 for r in runs if r.get("conclusion") == "failure")
        cancelled_runs = sum(1 for r in runs if r.get("conclusion") == "cancelled")
        
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        cancellation_rate = (cancelled_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Calculate runtimes
        durations = [r.get("durationMinutes", 0) for r in runs if r.get("durationMinutes")]
        average_runtime_seconds = int((sum(durations) / len(durations) * 60)) if durations else 0
        
        sorted_durations = sorted(durations)
        p95_idx = max(0, int(len(sorted_durations) * 0.95) - 1)
        p95_runtime_seconds = int(sorted_durations[p95_idx] * 60) if sorted_durations else 0
        
        # Get last run
        last_run = runs[0] if runs else {}
        last_run_status = last_run.get("conclusion", "unknown")
        last_run_timestamp = last_run.get("createdAt", datetime.utcnow().isoformat())
        last_run_duration = int(last_run.get("durationMinutes", 0) * 60)
        
        # Calculate flakiness (retry rate / instability)
        flakiness_score = 0.0
        if success_rate > 0:
            failure_ratio = (failed_runs / total_runs)
            flakiness_score = min(1.0, failure_ratio * 2)  # Normalized 0-1

        # Determine trend (comparing first half vs second half)
        mid = len(runs) // 2
        if mid > 0:
            first_half_success = sum(1 for r in runs[:mid] if r.get("conclusion") == "success") / mid * 100
            second_half_success = sum(1 for r in runs[mid:] if r.get("conclusion") == "success") / (total_runs - mid) * 100
            
            if second_half_success > first_half_success + 5:
                trend = "improving"
            elif second_half_success < first_half_success - 5:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return WorkflowMetrics(
            workflow_name=workflow_name,
            workflow_path=workflow_path,
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            cancelled_runs=cancelled_runs,
            success_rate=round(success_rate, 2),
            average_runtime_seconds=average_runtime_seconds,
            p95_runtime_seconds=p95_runtime_seconds,
            cancellation_rate=round(cancellation_rate, 2),
            flakiness_score=round(flakiness_score, 3),
            last_run_status=last_run_status,
            last_run_timestamp=last_run_timestamp,
            last_run_duration_seconds=last_run_duration,
            trend=trend,
            critical_alerts=0,  # TODO: Integrate CodeQL
            high_alerts=0  # TODO: Integrate CodeQL
        )

    def collect_all_metrics(self, days: int = 30) -> Dict[str, WorkflowMetrics]:
        """Collect metrics for all workflows"""
        workflows = self.get_workflows()
        metrics = {}
        
        for workflow in workflows:
            workflow_id = str(workflow.get("id"))
            workflow_name = workflow.get("name", "unknown")
            workflow_path = workflow.get("path", "")
            
            logger.info(f"Collecting metrics for {workflow_name}...")
            
            workflow_metrics = self.calculate_metrics(workflow_id, workflow_name, workflow_path, days)
            if workflow_metrics:
                metrics[workflow_name] = workflow_metrics
            else:
                logger.warning(f"Skipping {workflow_name} (no metrics)")

        return metrics

    def save_snapshot(self, metrics: Dict[str, WorkflowMetrics], output_file: str):
        """Save metrics snapshot to JSON"""
        logger.info(f"Saving snapshot to {output_file}...")
        
        snapshot = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "metrics": {k: asdict(v) for k, v in metrics.items()},
            "summary": self._generate_summary(metrics)
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(snapshot, f, indent=2)
        
        logger.info(f"Snapshot saved ({len(metrics)} workflows)")

    def _generate_summary(self, metrics: Dict[str, WorkflowMetrics]) -> Dict:
        """Generate summary statistics"""
        if not metrics:
            return {}

        success_rates = [m.success_rate for m in metrics.values()]
        runtimes = [m.average_runtime_seconds for m in metrics.values()]
        
        return {
            "total_workflows": len(metrics),
            "avg_success_rate": round(sum(success_rates) / len(success_rates), 2) if success_rates else 0,
            "min_success_rate": min(success_rates) if success_rates else 0,
            "max_success_rate": max(success_rates) if success_rates else 0,
            "avg_runtime_seconds": sum(runtimes) // len(runtimes) if runtimes else 0,
            "workflows_above_95_percent": sum(1 for r in success_rates if r >= 95),
            "workflows_below_80_percent": sum(1 for r in success_rates if r < 80),
            "total_runtime_hours": sum(runtimes) // 3600 if runtimes else 0
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect workflow health metrics")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze")
    parser.add_argument("--workflow", type=str, help="Specific workflow to analyze")
    parser.add_argument("--output", type=str, default=".codex/workflow_health_snapshot.json", help="Output file")
    parser.add_argument("--repo", type=str, help="Repository (owner/repo)")
    
    args = parser.parse_args()
    
    if args.repo:
        os.environ["GITHUB_REPOSITORY"] = args.repo

    collector = WorkflowHealthCollector()
    
    if not collector.gh_cli_available:
        logger.error("gh CLI not available. Install it first: https://cli.github.com/")
        sys.exit(1)

    try:
        metrics = collector.collect_all_metrics(days=args.days)
        collector.save_snapshot(metrics, args.output)
        logger.info("✅ Metrics collection complete")
        
        # Print summary
        summary = collector._generate_summary(metrics)
        print("\n📊 Summary:")
        print(f"  Total Workflows: {summary.get('total_workflows', 0)}")
        print(f"  Avg Success Rate: {summary.get('avg_success_rate', 0)}%")
        print(f"  Workflows >95%: {summary.get('workflows_above_95_percent', 0)}")
        print(f"  Workflows <80%: {summary.get('workflows_below_80_percent', 0)}")
        
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Collection failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
