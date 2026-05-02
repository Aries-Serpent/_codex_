#!/usr/bin/env python3
"""
Workflow Monitoring Utility
Monitors GitHub Actions workflows and tracks their status over time.

Usage:
    python scripts/monitoring/workflow_monitor.py --duration 55 --interval 5
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class WorkflowMonitor:
    """Monitor GitHub Actions workflows for a specified duration."""

    def __init__(self, owner: str, repo: str, branch: str, duration_minutes: int, check_interval_minutes: int):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.duration_minutes = duration_minutes
        self.check_interval_minutes = check_interval_minutes
        self.start_time = datetime.now(timezone.utc)
        self.monitoring_log: List[Dict[str, Any]] = []

    def get_workflow_runs(self) -> List[Dict[str, Any]]:
        """Get current workflow runs for the branch."""
        try:
            # Use GitHub API (would need gh CLI or API token in production)
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            print(f"Error fetching workflow runs: {e}")
            return []

    def analyze_workflow_status(self, run: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a workflow run and categorize its status."""
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', 'N/A')

        return {
            'id': run.get('id'),
            'name': run.get('name'),
            'status': status,
            'conclusion': conclusion,
            'created_at': run.get('created_at'),
            'updated_at': run.get('updated_at'),
            'url': run.get('html_url'),
            'category': self._categorize_status(status, conclusion),
            'requires_action': conclusion == 'action_required',
            'failed': conclusion == 'failure',
            'passed': conclusion == 'success',
        }


    def _categorize_status(self, status: str, conclusion: str) -> str:
        """Categorize workflow status for reporting."""
        if status == 'in_progress':
            return 'RUNNING'
        if status == 'completed':
            if conclusion == 'success':
                return 'SUCCESS'
            if conclusion == 'failure':
                return 'FAILURE'
            if conclusion == 'action_required':
                return 'AWAITING_ACTION'
            if conclusion == 'skipped':
                return 'SKIPPED'
            return 'COMPLETED_UNKNOWN'
        if status == 'queued':
            return 'QUEUED'
        return 'UNKNOWN'

    def check_workflows(self) -> Dict[str, Any]:
        """Perform a workflow status check."""
        timestamp = datetime.now(timezone.utc)
        elapsed_minutes = (timestamp - self.start_time).total_seconds() / 60

        runs = self.get_workflow_runs()
        analyses = [self.analyze_workflow_status(run) for run in runs]

        summary = {
            'timestamp': timestamp.isoformat(),
            'elapsed_minutes': round(elapsed_minutes, 2),
            'total_workflows': len(analyses),
            'running': sum(1 for a in analyses if a['category'] == 'RUNNING'),
            'failed': sum(1 for a in analyses if a['failed']),
            'passed': sum(1 for a in analyses if a['passed']),
            'awaiting_action': sum(1 for a in analyses if a['requires_action']),
            'skipped': sum(1 for a in analyses if a['category'] == 'SKIPPED'),
            'workflows': analyses,
        }

        self.monitoring_log.append(summary)
        return summary

    def display_summary(self, summary: Dict[str, Any]) -> None:
        """Display a formatted summary of the check."""
        print("\n" + "="*80)
        print(f"Workflow Status Check - {summary['timestamp']}")
        print(f"Elapsed: {summary['elapsed_minutes']:.2f} / {self.duration_minutes} minutes")
        print("="*80)
        print(f"Total Workflows: {summary['total_workflows']}")
        print(f"  ▶ Running: {summary['running']}")
        print(f"  ✓ Passed: {summary['passed']}")
        print(f"  ✗ Failed: {summary['failed']}")
        print(f"  ⚠ Awaiting Action: {summary['awaiting_action']}")
        print(f"  ⊘ Skipped: {summary['skipped']}")
        print("-"*80)

        for workflow in summary['workflows']:
            icon = self._get_status_icon(workflow['category'])
            print(f"{icon} {workflow['name']:<40s} | {workflow['category']:<15s}")

    def _get_status_icon(self, category: str) -> str:
        """Get icon for workflow category."""
        icons = {
            'RUNNING': '▶',
            'SUCCESS': '✓',
            'FAILURE': '✗',
            'AWAITING_ACTION': '⚠',
            'SKIPPED': '⊘',
            'QUEUED': '⏳',
            'UNKNOWN': '?',
        }
        return icons.get(category, '•')

    def save_report(self, output_path: Path) -> None:
        """Save monitoring report to file."""
        report = {
            'monitoring_config': {
                'owner': self.owner,
                'repo': self.repo,
                'branch': self.branch,
                'duration_minutes': self.duration_minutes,
                'check_interval_minutes': self.check_interval_minutes,
                'start_time': self.start_time.isoformat(),
            },
            'checks': self.monitoring_log,
            'summary': self._generate_final_summary(),
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Report saved to: {output_path}")

    def _generate_final_summary(self) -> Dict[str, Any]:
        """Generate final summary statistics."""
        if not self.monitoring_log:
            return {}

        last_check = self.monitoring_log[-1]
        return {
            'total_checks': len(self.monitoring_log),
            'final_status': last_check,
            'failures_detected': any(check['failed'] > 0 for check in self.monitoring_log),
            'completion_time': datetime.now(timezone.utc).isoformat(),
        }

    def run(self) -> None:
        """Run the monitoring loop."""
        print("\n🔍 Starting Workflow Monitor")
        print(f"   Repository: {self.owner}/{self.repo}")
        print(f"   Branch: {self.branch}")
        print(f"   Duration: {self.duration_minutes} minutes")
        print(f"   Check Interval: {self.check_interval_minutes} minutes")
        print(f"   Start Time: {self.start_time.isoformat()}")

        check_count = 0
        while True:
            check_count += 1
            elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 60

            if elapsed >= self.duration_minutes:
                print(f"\n✓ Monitoring duration reached ({self.duration_minutes} minutes)")
                break

            summary = self.check_workflows()
            self.display_summary(summary)

            remaining = self.duration_minutes - elapsed
            if remaining > self.check_interval_minutes:
                print(f"\n⏱ Next check in {self.check_interval_minutes} minutes...")
                print(f"   Remaining: {remaining:.2f} minutes")
                time.sleep(self.check_interval_minutes * 60)
            else:
                break

        # Save final report
        output_path = Path('.codex/workflow_monitoring_results.json')
        self.save_report(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Monitor GitHub Actions workflows over time'
    )
    parser.add_argument(
        '--owner',
        default='Aries-Serpent',
        help='Repository owner (default: Aries-Serpent)'
    )
    parser.add_argument(
        '--repo',
        default='_codex_',
        help='Repository name (default: _codex_)'
    )
    parser.add_argument(
        '--branch',
        default='copilot/monitor-workflows-and-develop-solutions',
        help='Branch to monitor'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=55,
        help='Monitoring duration in minutes (default: 55)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Check interval in minutes (default: 5)'
    )

    args = parser.parse_args()

    monitor = WorkflowMonitor(
        owner=args.owner,
        repo=args.repo,
        branch=args.branch,
        duration_minutes=args.duration,
        check_interval_minutes=args.interval
    )

    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n\n⚠ Monitoring interrupted by user")
        output_path = Path('.codex/workflow_monitoring_results_interrupted.json')
        monitor.save_report(output_path)
        sys.exit(1)


if __name__ == '__main__':
    main()
