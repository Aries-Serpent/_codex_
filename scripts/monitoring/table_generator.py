#!/usr/bin/env python3
"""
Table Generator - Rich Markdown table formatting for GitHub Issues.

This module provides utilities for generating well-formatted Markdown tables
with diagnostic links, metrics, and other information for workflow failures.

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TableGenerator:
    """Generates rich Markdown tables for issue formatting."""

    def __init__(self):
        """Initialize table generator."""

    def generate_summary_table(self, run: Any, workflow_name: str) -> str:
        """
        Generate summary table with key workflow run information.

        Args:
            run: GitHub WorkflowRun object
            workflow_name: Name of the workflow

        Returns:
            Markdown table string
        """
        # Extract run information
        run_id = run.id
        branch = run.head_branch
        commit_sha = run.head_sha[:7] if run.head_sha else 'unknown'
        started = run.created_at.isoformat() if run.created_at else 'Unknown'

        # Calculate duration
        duration = self._format_duration(run.run_duration_ms / 1000 if run.run_duration_ms else 0)

        # Get trigger event
        event = run.event

        return f"""| Metric | Value |
|--------|-------|
| **Workflow** | {workflow_name} |
| **Run ID** | [#{run_id}]({run.html_url}) |
| **Branch** | {branch} |
| **Commit** | {commit_sha} |
| **Started** | {started} |
| **Duration** | {duration} |
| **Triggered By** | {event} |"""


    def generate_diagnostic_links_table(self, run: Any) -> str:
        """
        Generate table with links to logs, artifacts, and other diagnostic resources.

        Args:
            run: GitHub WorkflowRun object

        Returns:
            Markdown table string
        """
        run_id = run.id
        repo_url = run.repository.html_url if run.repository else ''

        # Build diagnostic URLs
        run_url = run.html_url
        logs_url = f"{run_url}/logs" if run_url else '#'
        rerun_url = f"{run_url}/re-run-failed-jobs" if run_url else '#'

        # Artifacts URL (if available)
        artifacts_url = f"{repo_url}/actions/runs/{run_id}#artifacts" if repo_url else '#'

        return f"""| Resource | Link |
|----------|------|
| **Workflow Run** | [#{run_id}]({run_url}) |
| **Logs** | [View Logs]({logs_url}) |
| **Artifacts** | [Browse Artifacts]({artifacts_url}) |
| **Rerun** | [Rerun Failed Jobs]({rerun_url}) |"""


    def generate_metrics_table(self, metrics: Dict[str, Any]) -> str:
        """
        Generate table with failure metrics and statistics.

        Args:
            metrics: Dictionary of metrics

        Returns:
            Markdown table string
        """
        return f"""| Metric | Value |
|--------|-------|
| **Consecutive Failures** | {metrics.get('consecutive_failures', 0)} |
| **Failure Rate** | {metrics.get('failure_rate', 0):.1f}% |
| **Total Runs Analyzed** | {metrics.get('total_runs_analyzed', 0)} |
| **Total Failures** | {metrics.get('total_failures', 0)} |
| **Flakiness Score** | {metrics.get('flakiness_score', 0):.2f} |"""


    def generate_pattern_table(self, patterns: List[Dict[str, Any]]) -> str:
        """
        Generate table with matched error patterns.

        Args:
            patterns: List of matched patterns with confidence scores

        Returns:
            Markdown table string
        """
        if not patterns:
            return "_No patterns matched_"

        table = """| Pattern | Category | Confidence | Severity |
|---------|----------|------------|----------|
"""

        for pattern in patterns:
            name = pattern.get('name', 'Unknown')
            category = pattern.get('category', 'unknown')
            confidence = pattern.get('confidence', 0) * 100
            severity = pattern.get('severity', 'medium')

            table += f"| {name} | {category} | {confidence:.0f}% | {severity} |\n"

        return table

    def generate_agent_recommendations_table(self, recommendations: List[Dict[str, Any]]) -> str:
        """
        Generate table with agent recommendations.

        Args:
            recommendations: List of recommendations from specialized agents

        Returns:
            Markdown table string
        """
        if not recommendations:
            return "_No agent recommendations available_"

        table = """| Agent | Confidence | Recommendation |
|-------|------------|----------------|
"""

        for rec in recommendations:
            agent = rec.get('agent', 'Unknown Agent')
            confidence = rec.get('confidence', 0) * 100
            recommendation = rec.get('recommendation', 'No recommendation')[:100]  # Truncate

            table += f"| {agent} | {confidence:.0f}% | {recommendation}... |\n"

        return table

    def generate_run_history_table(self, runs: List[Any], limit: int = 10) -> str:
        """
        Generate table with recent run history.

        Args:
            runs: List of WorkflowRun objects
            limit: Maximum number of runs to include

        Returns:
            Markdown table string
        """
        if not runs:
            return "_No run history available_"

        table = """| Run | Time | Status | Duration |
|-----|------|--------|----------|
"""

        for run in runs[:limit]:
            run_id = run.id
            run_url = run.html_url
            time = run.created_at.strftime('%Y-%m-%d %H:%M') if run.created_at else 'Unknown'
            status = run.conclusion or run.status
            status_emoji = '✅' if status == 'success' else '❌' if status == 'failure' else '⏸️'
            duration = self._format_duration(run.run_duration_ms / 1000 if run.run_duration_ms else 0)

            table += f"| [#{run_id}]({run_url}) | {time} | {status_emoji} {status} | {duration} |\n"

        return table

    def generate_nested_links_table(
        self,
        run: Any,
        include_artifacts: bool = True,
        include_jobs: bool = True
    ) -> str:
        """
        Generate comprehensive table with nested links to all diagnostic resources.

        Args:
            run: GitHub WorkflowRun object
            include_artifacts: Include artifact links
            include_jobs: Include individual job links

        Returns:
            Markdown table string with nested structure
        """
        run_id = run.id
        repo_url = run.repository.html_url if run.repository else ''
        run_url = run.html_url

        table = """| Resource | Links |
|----------|-------|
"""

        # Workflow run
        table += f"| **Workflow Run** | [View Run]({run_url}) · [Logs]({run_url}/logs) · [Rerun]({run_url}/re-run-failed-jobs) |\n"

        # Jobs (if requested)
        if include_jobs:
            try:
                jobs = list(run.jobs())
                if jobs:
                    job_links = []
                    for job in jobs[:5]:  # Limit to first 5 jobs
                        status_emoji = '✅' if job.conclusion == 'success' else '❌' if job.conclusion == 'failure' else '⏸️'
                        job_links.append(f"[{status_emoji} {job.name}]({job.html_url})")
                    table += f"| **Jobs** | {' · '.join(job_links)} |\n"
            except Exception:
                logger.debug("Suppressed exception in handler", exc_info=True)
        # Artifacts (if requested)
        if include_artifacts:
            artifacts_url = f"{repo_url}/actions/runs/{run_id}#artifacts"
            table += f"| **Artifacts** | [Browse All]({artifacts_url}) |\n"

        # Advanced diagnostics
        table += f"| **Advanced** | [Raw Logs]({run_url}/logs?raw=1) · [Debug]({run_url}?debug=1) |\n"

        return table

    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        if seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:.0f}m {secs:.0f}s"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"

    def generate_comparison_table(
        self,
        current_run: Any,
        previous_success: Optional[Any] = None
    ) -> str:
        """
        Generate comparison table between current failure and last success.

        Args:
            current_run: Current failed run
            previous_success: Previous successful run (if available)

        Returns:
            Markdown table string
        """
        if not previous_success:
            return "_No previous success available for comparison_"

        current_duration = current_run.run_duration_ms / 1000 if current_run.run_duration_ms else 0
        previous_duration = previous_success.run_duration_ms / 1000 if previous_success.run_duration_ms else 0
        duration_diff = current_duration - previous_duration
        duration_pct = (duration_diff / previous_duration * 100) if previous_duration > 0 else 0

        return f"""| Metric | Current (Failed) | Previous (Success) | Change |
|--------|-----------------|-------------------|--------|
| **Run ID** | [#{current_run.id}]({current_run.html_url}) | [#{previous_success.id}]({previous_success.html_url}) | - |
| **Duration** | {self._format_duration(current_duration)} | {self._format_duration(previous_duration)} | {duration_diff:+.0f}s ({duration_pct:+.1f}%) |
| **Commit** | {current_run.head_sha[:7] if current_run.head_sha else 'N/A'} | {previous_success.head_sha[:7] if previous_success.head_sha else 'N/A'} | [Compare](https://github.com/{current_run.repository.full_name}/compare/{previous_success.head_sha}...{current_run.head_sha}) |
| **Time** | {current_run.created_at.strftime('%Y-%m-%d %H:%M') if current_run.created_at else 'N/A'} | {previous_success.created_at.strftime('%Y-%m-%d %H:%M') if previous_success.created_at else 'N/A'} | - |
"""

