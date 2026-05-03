#!/usr/bin/env python3
"""
Artifact Monitor - Core monitoring engine for GitHub Actions workflows.

This module provides the main monitoring functionality including:
- GitHub API client for workflow/run/artifact retrieval
- State management for tracking workflow statuses
- Failure detection with configurable thresholds
- Rate limit handling and exponential backoff

Usage:
    python scripts/monitoring/artifact_monitor.py --check
    python scripts/monitoring/artifact_monitor.py --workflow test-comprehensive.yml
    python scripts/monitoring/artifact_monitor.py --dry-run

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
    from github import Github, GithubException
    from github.WorkflowRun import WorkflowRun
except ImportError as e:
    raise ImportError(
        f"Required dependencies not installed: {e}. "
        "Install with: pip install PyGithub requests PyYAML"
    ) from e

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitorState:
    """Manages monitoring state persistence."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load state from file or create new state."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}. Creating new state.")

        return {
            'last_check_timestamp': None,
            'workflows': {},
            'stats': {
                'total_runs_checked': 0,
                'failures_detected': 0,
                'patterns_matched': 0,
                'issues_created': 0,
                'issues_closed': 0
            }
        }

    def save_state(self) -> None:
        """Save current state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        logger.debug(f"State saved to {self.state_file}")

    def get_workflow_state(self, workflow_name: str) -> dict[str, Any]:
        """Get state for specific workflow."""
        return self.state['workflows'].get(workflow_name, {})

    def update_workflow_state(self, workflow_name: str, data: dict[str, Any]) -> None:
        """Update state for specific workflow."""
        if workflow_name not in self.state['workflows']:
            self.state['workflows'][workflow_name] = {}
        self.state['workflows'][workflow_name].update(data)

    def update_stats(self, stat_name: str, increment: int = 1) -> None:
        """Update statistics counter."""
        if stat_name in self.state['stats']:
            self.state['stats'][stat_name] += increment
        else:
            self.state['stats'][stat_name] = increment


class ArtifactMonitor:
    """Main monitoring engine for GitHub Actions workflows."""

    def __init__(self, config_path: Path, state_path: Path, dry_run: bool = False):
        """
        Initialize artifact monitor.

        Args:
            config_path: Path to monitoring configuration YAML
            state_path: Path to state JSON file
            dry_run: If True, don't create issues or modify state
        """
        self.config = self._load_config(config_path)
        self.state = MonitorState(state_path)
        self.dry_run = dry_run

        # Initialize GitHub client
        token = os.getenv('GITHUB_TOKEN') or os.getenv('CODEX_MASTER_KEY')
        if not token:
            raise ValueError("GitHub token not found in GITHUB_TOKEN or CODEX_MASTER_KEY")

        self.github = Github(token)
        self.repo_name = os.getenv('GITHUB_REPOSITORY', 'Aries-Serpent/_codex_')
        self.repo = self.github.get_repo(self.repo_name)

        logger.info(f"Initialized monitor for repository: {self.repo_name}")
        logger.info(f"Dry run mode: {self.dry_run}")

    def _load_config(self, config_path: Path) -> dict[str, Any]:
        """Load monitoring configuration from YAML."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            return yaml.safe_load(f)


    def _matches_pattern(self, workflow_name: str, patterns: list[str]) -> bool:
        """Check if workflow name matches any pattern."""
        for pattern in patterns:
            # Convert glob-style pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            if re.match(regex_pattern, workflow_name):
                return True
        return False

    def _should_monitor_workflow(self, workflow_name: str) -> bool:
        """Determine if workflow should be monitored."""
        config = self.config['monitoring']['workflows']

        # Check exclusion patterns first
        if self._matches_pattern(workflow_name, config.get('exclude_patterns', [])):
            return False

        # Check inclusion patterns
        return bool(self._matches_pattern(workflow_name, config.get('include_patterns', [])))

    def _check_rate_limit(self) -> None:
        """Check GitHub API rate limit and wait if necessary."""
        rate_limit = self.github.get_rate_limit()
        core_remaining = rate_limit.core.remaining
        margin = self.config['monitoring']['failure_detection']['rate_limit_margin']

        if core_remaining < margin:
            reset_time = rate_limit.core.reset
            wait_seconds = (reset_time - datetime.now(timezone.utc)).total_seconds()
            logger.warning(
                f"Approaching rate limit ({core_remaining} remaining). "
                f"Waiting {wait_seconds:.0f}s until reset."
            )
            if wait_seconds > 0:
                time.sleep(wait_seconds + 10)  # Add 10s buffer

    def _get_workflow_runs(
        self,
        workflow_name: str,
        limit: int = 20
    ) -> list[WorkflowRun]:
        """Get recent runs for a workflow."""
        try:
            workflow = self.repo.get_workflow(workflow_name)
            runs = workflow.get_runs()
            return list(runs[:limit])
        except GithubException as e:
            logger.error(f"Failed to get runs for {workflow_name}: {e}")
            return []

    def _detect_status_change(
        self,
        workflow_name: str,
        current_run: WorkflowRun
    ) -> tuple[bool, str, str]:
        """
        Detect if workflow status has changed.

        Returns:
            (changed, old_status, new_status)
        """
        workflow_state = self.state.get_workflow_state(workflow_name)
        old_status = workflow_state.get('status', 'unknown')
        new_status = current_run.conclusion or current_run.status

        changed = old_status != new_status
        return changed, old_status, new_status

    def _calculate_failure_metrics(
        self,
        runs: list[WorkflowRun]
    ) -> dict[str, Any]:
        """Calculate failure rate and flakiness metrics."""
        if not runs:
            return {'failure_rate': 0.0, 'flakiness_score': 0.0, 'consecutive_failures': 0}

        # Count failures
        failures = sum(1 for run in runs if run.conclusion == 'failure')
        failure_rate = failures / len(runs) * 100

        # Calculate consecutive failures from most recent
        consecutive_failures = 0
        for run in runs:
            if run.conclusion == 'failure':
                consecutive_failures += 1
            else:
                break

        # Calculate flakiness score (simplified)
        # Real implementation would analyze time intervals between failures
        if len(runs) >= 10:
            # Check for intermittent failures
            failure_pattern = [1 if run.conclusion == 'failure' else 0 for run in runs[:10]]
            if 0 < sum(failure_pattern) < 10:
                flakiness_score = 1.0 - abs(sum(failure_pattern) / 10 - 0.5) * 2
            else:
                flakiness_score = 0.0
        else:
            flakiness_score = 0.0

        return {
            'failure_rate': failure_rate,
            'flakiness_score': flakiness_score,
            'consecutive_failures': consecutive_failures,
            'total_runs_analyzed': len(runs),
            'total_failures': failures
        }

    def _should_create_issue(
        self,
        workflow_name: str,
        metrics: dict[str, Any]
    ) -> bool:
        """Determine if an issue should be created for this failure."""
        threshold = self.config['monitoring']['failure_detection']['consecutive_failures_threshold']

        # Check if consecutive failures exceed threshold
        if metrics['consecutive_failures'] < threshold:
            logger.debug(
                f"{workflow_name}: Only {metrics['consecutive_failures']} consecutive failures "
                f"(threshold: {threshold})"
            )
            return False

        # Check if issue already exists for this workflow
        workflow_state = self.state.get_workflow_state(workflow_name)
        if workflow_state.get('issue_number'):
            logger.debug(f"{workflow_name}: Issue already exists (#{workflow_state['issue_number']})")
            return False

        return True

    def check_workflow(self, workflow_name: str) -> Optional[dict[str, Any]]:
        """
        Check a single workflow for failures.

        Returns:
            Failure data if detected, None otherwise
        """
        logger.info(f"Checking workflow: {workflow_name}")

        # Check rate limit
        self._check_rate_limit()

        # Get recent runs
        runs = self._get_workflow_runs(workflow_name)
        if not runs:
            logger.warning(f"No runs found for {workflow_name}")
            return None

        latest_run = runs[0]

        # Detect status change
        changed, old_status, new_status = self._detect_status_change(workflow_name, latest_run)

        logger.info(
            f"{workflow_name}: status={new_status}, changed={changed}, "
            f"run_id={latest_run.id}"
        )

        # Update state
        self.state.update_workflow_state(workflow_name, {
            'last_run_id': latest_run.id,
            'status': new_status,
            'last_check': datetime.now(timezone.utc).isoformat()
        })

        # Only process failures
        if new_status != 'failure':
            # Check if workflow recovered
            if old_status == 'failure' and new_status == 'success':
                logger.info(f"{workflow_name}: Workflow recovered!")
                return {
                    'workflow_name': workflow_name,
                    'event': 'recovered',
                    'run': latest_run
                }
            return None

        # Calculate metrics
        metrics = self._calculate_failure_metrics(runs)

        # Determine if issue should be created
        should_create = self._should_create_issue(workflow_name, metrics)

        if should_create:
            logger.warning(
                f"{workflow_name}: FAILURE DETECTED - "
                f"consecutive: {metrics['consecutive_failures']}, "
                f"rate: {metrics['failure_rate']:.1f}%"
            )

            return {
                'workflow_name': workflow_name,
                'event': 'failure_detected',
                'run': latest_run,
                'metrics': metrics,
                'runs': runs[:5]  # Include last 5 runs for context
            }

        return None

    def check_all_workflows(self) -> list[dict[str, Any]]:
        """
        Check all monitored workflows.

        Returns:
            List of failure/recovery events
        """
        logger.info("Starting workflow monitoring check...")

        # Update last check timestamp
        self.state.state['last_check_timestamp'] = datetime.now(timezone.utc).isoformat()

        # Load workflow inventory
        inventory_path = Path('.codex/monitoring/workflow_inventory.json')
        if not inventory_path.exists():
            logger.error("Workflow inventory not found. Run discovery first.")
            return []

        with open(inventory_path) as f:
            inventory = json.load(f)

        events = []
        workflows_checked = 0

        for workflow_data in inventory['workflows']:
            workflow_name = Path(workflow_data['path']).name

            # Check if should be monitored
            if not self._should_monitor_workflow(workflow_name):
                logger.debug(f"Skipping {workflow_name} (not in monitor list)")
                continue

            try:
                event = self.check_workflow(workflow_name)
                if event:
                    events.append(event)
                workflows_checked += 1

            except Exception as e:
                logger.error(f"Error checking {workflow_name}: {e}")

        # Update stats
        self.state.update_stats('total_runs_checked', workflows_checked)
        self.state.update_stats('failures_detected', len([e for e in events if e['event'] == 'failure_detected']))

        # Save state
        if not self.dry_run:
            self.state.save_state()

        logger.info(
            f"Monitoring check complete. "
            f"Checked: {workflows_checked}, "
            f"Failures: {len([e for e in events if e['event'] == 'failure_detected'])}, "
            f"Recoveries: {len([e for e in events if e['event'] == 'recovered'])}"
        )

        return events


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='GitHub Actions Artifact Monitor')
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('.codex/config/monitoring.yaml'),
        help='Path to monitoring configuration'
    )
    parser.add_argument(
        '--state',
        type=Path,
        default=Path('.codex/monitoring/state/monitor_state.json'),
        help='Path to state file'
    )
    parser.add_argument(
        '--workflow',
        help='Check specific workflow only'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without creating issues or modifying state'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        monitor = ArtifactMonitor(args.config, args.state, args.dry_run)

        if args.workflow:
            # Check single workflow
            event = monitor.check_workflow(args.workflow)
            if event:
                print(json.dumps(event, indent=2, default=str))
            else:
                print(f"No events detected for {args.workflow}")
        else:
            # Check all workflows
            events = monitor.check_all_workflows()
            print(f"\n{'='*60}")
            print("Monitoring Summary:")
            print(f"{'='*60}")
            print(f"Total events: {len(events)}")
            print(f"Failures: {len([e for e in events if e['event'] == 'failure_detected'])}")
            print(f"Recoveries: {len([e for e in events if e['event'] == 'recovered'])}")

            if events:
                print("\nEvents:")
                for event in events:
                    print(f"  - {event['workflow_name']}: {event['event']}")

        return 0

    except Exception as e:
        logger.error(f"Monitor failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
