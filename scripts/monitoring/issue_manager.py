#!/usr/bin/env python3
"""
Issue Manager - Handles GitHub Issue lifecycle for workflow failures.

This module provides functionality for:
- Creating issues for detected failures
- Updating existing issues with new information
- Closing issues when workflows recover
- Deduplicating similar failures
- Rich formatting with diagnostic links

Usage:
    from scripts.monitoring.issue_manager import IssueManager

    manager = IssueManager(github_client, config)
    manager.create_failure_issue(failure_data)
    manager.close_recovery_issue(workflow_name)

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""

import logging
from typing import Any, Optional

from github import Github
from github.Issue import Issue
from github.Repository import Repository

from .table_generator import TableGenerator

logger = logging.getLogger(__name__)


class IssueManager:
    """Manages GitHub Issues for workflow failures."""

    def __init__(self, github: Github, repo: Repository, config: dict[str, Any], dry_run: bool = False):
        """
        Initialize issue manager.

        Args:
            github: GitHub API client
            repo: GitHub repository object
            config: Monitoring configuration
            dry_run: If True, don't actually create/update issues
        """
        self.github = github
        self.repo = repo
        self.config = config
        self.dry_run = dry_run
        self.table_gen = TableGenerator()

        logger.info(f"IssueManager initialized for {repo.full_name}, dry_run={dry_run}")

    def _find_existing_issue(self, workflow_name: str) -> Optional[Issue]:
        """
        Find existing open issue for a workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Existing issue or None
        """
        # Search for issues with workflow name in title
        query = f"repo:{self.repo.full_name} is:issue is:open \"{workflow_name}\" in:title"

        try:
            issues = self.github.search_issues(query)
            for issue in issues:
                # Check if it's an auto-generated issue
                if '[AUTO-MONITOR]' in issue.title and workflow_name in issue.title:
                    logger.debug(f"Found existing issue for {workflow_name}: #{issue.number}")
                    return issue
        except Exception as e:
            logger.error(f"Failed to search for existing issues: {e}")

        return None

    def _generate_issue_title(self, workflow_name: str) -> str:
        """Generate issue title."""
        template = self.config['monitoring']['issue_management']['title_template']
        return template.format(workflow_name=workflow_name)

    def _generate_labels(self, failure_data: dict[str, Any]) -> list[str]:
        """Generate appropriate labels for the issue."""
        labels = list(self.config['monitoring']['issue_management']['labels'])

        # Add severity label if enabled
        if self.config['monitoring']['issue_management'].get('add_severity_labels'):
            metrics = failure_data.get('metrics', {})
            consecutive = metrics.get('consecutive_failures', 0)
            failure_rate = metrics.get('failure_rate', 0)

            if consecutive >= 5 or failure_rate > 50:
                labels.append('severity:high')
            elif consecutive >= 3 or failure_rate > 25:
                labels.append('severity:medium')
            else:
                labels.append('severity:low')

        # Add category label if available (from pattern matching)
        if self.config['monitoring']['issue_management'].get('add_category_labels'):
            category = failure_data.get('pattern', {}).get('category')
            if category:
                labels.append(f'category:{category}')

        return labels

    def _generate_issue_body(self, failure_data: dict[str, Any]) -> str:
        """Generate comprehensive issue body with rich formatting."""
        workflow_name = failure_data['workflow_name']
        run = failure_data['run']
        metrics = failure_data.get('metrics', {})

        # Calculate some additional info
        last_success_time = self._find_last_success_time(failure_data.get('runs', []))

        body = f"""# Workflow Failure: {workflow_name}

**Status**: ❌ FAILED ({metrics.get('consecutive_failures', 1)} consecutive failures)
**Last Success**: {last_success_time or 'Unknown'}
**Failure Rate**: {metrics.get('failure_rate', 0):.1f}% ({metrics.get('total_failures', 0)}/{metrics.get('total_runs_analyzed', 0)} recent runs)

---

## 📊 Failure Summary

{self.table_gen.generate_summary_table(run, workflow_name)}

---

## 🔗 Diagnostic Links

{self.table_gen.generate_diagnostic_links_table(run)}

---

## 🔍 Pattern Analysis

"""

        # Add pattern analysis if available
        if 'pattern' in failure_data:
            pattern = failure_data['pattern']
            body += f"""### Matched Pattern (Confidence: {pattern.get('confidence', 0) * 100:.0f}%)

#### {pattern.get('name', 'Unknown Pattern')}
- **ID**: `{pattern.get('id', 'N/A')}`
- **Category**: {pattern.get('category', 'unknown')}
- **Severity**: {pattern.get('severity', 'medium')}

**Suggested Fix**:
{pattern.get('suggestion', 'No suggestion available')}

"""
            if pattern.get('documentation'):
                body += f"**Documentation**: {pattern['documentation']}\n\n"
        else:
            body += "_Pattern analysis will be added by Pattern Analyzer component._\n\n"

        body += "---\n\n"

        # Add agent analysis section
        body += """## 🤖 Agent Analysis

_Agent analysis will be added by Agent Orchestrator component._

---

"""

        # Add historical context
        body += f"""## 📈 Historical Context

- **First Occurrence**: {run.created_at.isoformat()}
- **Failure Count**: {metrics.get('consecutive_failures', 1)} consecutive failures
- **Last Success**: {last_success_time or 'Unknown'}
- **Flakiness Score**: {metrics.get('flakiness_score', 0):.2f} {'(flaky test suspected)' if metrics.get('flakiness_score', 0) > 0.3 else '(not flaky)'}
- **Average Duration**: {self._format_duration(run.run_duration_ms / 1000 if run.run_duration_ms else 0)}

---

## ✅ Recommended Actions

1. **Immediate**: Review workflow logs and identify root cause
2. **Short-term**: Apply fix based on pattern analysis
3. **Long-term**: Add monitoring and tests to prevent recurrence

---

**Auto-generated by Artifact Monitor Agent** | [Configuration](.codex/config/monitoring.yaml) | [Architecture](.codex/monitoring/ARCHITECTURE.md)

_This issue will be automatically updated with new information and closed when the workflow recovers._
"""

        return body

    def _find_last_success_time(self, runs: list[Any]) -> Optional[str]:
        """Find the timestamp of the last successful run."""
        for run in runs:
            if run.conclusion == 'success':
                return run.created_at.isoformat()
        return None

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        if seconds < 3600:
            return f"{seconds / 60:.0f}m {seconds % 60:.0f}s"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"

    def create_failure_issue(self, failure_data: dict[str, Any]) -> Optional[Issue]:
        """
        Create a new issue for a workflow failure.

        Args:
            failure_data: Failure information including workflow name, run, metrics

        Returns:
            Created issue or None
        """
        workflow_name = failure_data['workflow_name']

        # Check for existing issue
        existing = self._find_existing_issue(workflow_name)
        if existing:
            logger.info(f"Issue already exists for {workflow_name}: #{existing.number}")
            return self.update_failure_issue(existing, failure_data)

        # Generate issue content
        title = self._generate_issue_title(workflow_name)
        body = self._generate_issue_body(failure_data)
        labels = self._generate_labels(failure_data)

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would create issue: {title}")
            logger.debug(f"[DRY-RUN] Labels: {labels}")
            logger.debug(f"[DRY-RUN] Body preview: {body[:200]}...")
            return None

        try:
            # Create issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )

            logger.info(f"✅ Created issue #{issue.number}: {title}")
            return issue

        except Exception as e:
            logger.error(f"Failed to create issue for {workflow_name}: {e}")
            return None

    def update_failure_issue(self, issue: Issue, failure_data: dict[str, Any]) -> Issue:
        """
        Update an existing issue with new failure information.

        Args:
            issue: Existing GitHub issue
            failure_data: New failure information

        Returns:
            Updated issue
        """
        workflow_name = failure_data['workflow_name']
        run = failure_data['run']
        metrics = failure_data.get('metrics', {})

        comment = f"""## 🔄 Failure Update

**Run**: #{run.id}
**Time**: {run.created_at.isoformat()}
**Consecutive Failures**: {metrics.get('consecutive_failures', 1)}
**Failure Rate**: {metrics.get('failure_rate', 0):.1f}%

{self.table_gen.generate_diagnostic_links_table(run)}

_This is an automated update from the Artifact Monitor Agent._
"""

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would update issue #{issue.number} for {workflow_name}")
            logger.debug(f"[DRY-RUN] Comment: {comment[:200]}...")
            return issue

        try:
            issue.create_comment(comment)
            logger.info(f"✅ Updated issue #{issue.number} with new failure information")
            return issue

        except Exception as e:
            logger.error(f"Failed to update issue #{issue.number}: {e}")
            return issue

    def close_recovery_issue(self, workflow_name: str, recovery_data: dict[str, Any]) -> bool:
        """
        Close an issue when workflow recovers.

        Args:
            workflow_name: Name of the workflow
            recovery_data: Recovery information

        Returns:
            True if issue was closed, False otherwise
        """
        # Find existing issue
        issue = self._find_existing_issue(workflow_name)
        if not issue:
            logger.debug(f"No open issue found for {workflow_name}")
            return False

        run = recovery_data['run']

        comment = f"""## ✅ Workflow Recovered

The workflow has recovered and is now passing!

**Recovery Run**: #{run.id}
**Time**: {run.created_at.isoformat()}
**Status**: {run.conclusion}

{self.table_gen.generate_diagnostic_links_table(run)}

This issue is being automatically closed. If the failure recurs, a new issue will be created.

---

**Auto-closed by Artifact Monitor Agent**
"""

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would close issue #{issue.number} for {workflow_name}")
            logger.debug(f"[DRY-RUN] Comment: {comment[:200]}...")
            return False

        try:
            # Add recovery comment
            issue.create_comment(comment)

            # Close issue
            issue.edit(state='closed')

            logger.info(f"✅ Closed issue #{issue.number} for recovered workflow: {workflow_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to close issue #{issue.number}: {e}")
            return False

    def deduplicate_issues(self, workflow_name: str) -> int:
        """
        Find and close duplicate issues for a workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Number of duplicate issues closed
        """
        query = f"repo:{self.repo.full_name} is:issue is:open \"{workflow_name}\" in:title"

        try:
            issues = list(self.github.search_issues(query))

            # Filter for auto-generated issues
            auto_issues = [
                issue for issue in issues
                if '[AUTO-MONITOR]' in issue.title and workflow_name in issue.title
            ]

            if len(auto_issues) <= 1:
                return 0

            # Keep the most recent, close the rest
            auto_issues.sort(key=lambda i: i.created_at, reverse=True)
            to_close = auto_issues[1:]

            closed_count = 0
            for issue in to_close:
                if self.dry_run:
                    logger.info(f"[DRY-RUN] Would close duplicate issue #{issue.number}")
                else:
                    try:
                        issue.create_comment("Closing as duplicate. Consolidated into a newer issue.")
                        issue.edit(state='closed', labels=issue.labels + ['duplicate'])
                        closed_count += 1
                        logger.info(f"Closed duplicate issue #{issue.number}")
                    except Exception as e:
                        logger.error(f"Failed to close duplicate issue #{issue.number}: {e}")

            return closed_count

        except Exception as e:
            logger.error(f"Failed to deduplicate issues for {workflow_name}: {e}")
            return 0
