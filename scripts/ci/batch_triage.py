#!/usr/bin/env python3
"""
Batch CI Failure Triage Tool

Purpose:
    Automate batch triage of post-merge CI/test failures, grouping issues by
    root cause and generating actionable remediation suggestions.

Usage:
    python scripts/ci/batch_triage.py --issues 2905,2906,2907,2908,2909,2910,2912,2913,2914,2915
    python scripts/ci/batch_triage.py --from-file links_extraction.csv
    python scripts/ci/batch_triage.py --workflow-runs 21145572518,21145583258 --output report.md

Arguments:
    --issues: Comma-separated GitHub issue numbers
    --from-file: CSV file with issue/workflow data (columns: issue_num, issue_url, workflow_run, analysis_run)
    --workflow-runs: Comma-separated workflow run IDs
    --output: Output file path (default: batch_triage_report.md)
    --json: Output as JSON instead of markdown
    --group-by: Grouping strategy (root_cause, workflow, severity) [default: root_cause]
    --auto-remediate: Enable auto-remediation suggestions

Environment Variables:
    GITHUB_TOKEN: GitHub API token for fetching workflow data
    GH_TOKEN: Alternative name for GITHUB_TOKEN

Dependencies:
    PyYAML, requests (optional - uses GitHub CLI if available)

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-19
"""

import argparse
import csv
import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directories to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from agents.self_healing import (
        IssueType, IssueSeverity, DetectedIssue,
        RemediationAction, SelfHealingEngine
    )
except ImportError:
    logger.warning("Could not import self-healing modules - limited functionality")
    IssueType = None
    IssueSeverity = None
    DetectedIssue = None
    RemediationAction = None
    SelfHealingEngine = None


@dataclass
class FailureRecord:
    """Record of a CI/test failure"""
    issue_number: int
    issue_url: str
    workflow_run_id: str
    analysis_run_id: Optional[str] = None
    workflow_name: Optional[str] = None
    failure_type: Optional[str] = None
    root_cause: Optional[str] = None
    severity: str = "medium"
    logs: Optional[str] = None
    detected_issues: List[Dict[str, Any]] = field(default_factory=list)
    suggested_actions: List[Dict[str, Any]] = field(default_factory=list)
    grouped_with: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TriageGroup:
    """Group of related failures"""
    group_id: str
    root_cause: str
    severity: str
    failure_count: int
    failures: List[FailureRecord] = field(default_factory=list)
    common_patterns: List[str] = field(default_factory=list)
    remediation_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'group_id': self.group_id,
            'root_cause': self.root_cause,
            'severity': self.severity,
            'failure_count': self.failure_count,
            'failures': [f.to_dict() for f in self.failures],
            'common_patterns': self.common_patterns,
            'remediation_suggestions': self.remediation_suggestions,
        }


class BatchTriageEngine:
    """Engine for batch triage of CI failures"""
    
    def __init__(self, repo: str = "Aries-Serpent/_codex_"):
        self.repo = repo
        self.owner, self.repo_name = repo.split('/')
        self.failures: List[FailureRecord] = []
        self.groups: List[TriageGroup] = []
        self.gh_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        
        # Initialize self-healing engine if available
        self.healing_engine = None
        if SelfHealingEngine:
            try:
                self.healing_engine = SelfHealingEngine(repo_root=REPO_ROOT)
            except Exception as e:
                logger.warning(f"Could not initialize self-healing engine: {e}")
    
    def fetch_workflow_logs(self, run_id: str) -> Optional[str]:
        """Fetch workflow run logs using GitHub CLI"""
        try:
            cmd = ['gh', 'run', 'view', run_id, '--log', '--repo', self.repo]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning(f"Failed to fetch logs for run {run_id}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout fetching logs for run {run_id}")
            return None
        except FileNotFoundError:
            logger.error("GitHub CLI (gh) not found - cannot fetch logs")
            return None
        except Exception as e:
            logger.error(f"Error fetching logs for run {run_id}: {e}")
            return None
    
    def fetch_issue_data(self, issue_num: int) -> Optional[Dict[str, Any]]:
        """Fetch GitHub issue data using GitHub CLI"""
        try:
            cmd = ['gh', 'issue', 'view', str(issue_num), '--json',
                   'title,body,state,labels,createdAt,updatedAt', '--repo', self.repo]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Failed to fetch issue {issue_num}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching issue {issue_num}: {e}")
            return None
    
    def analyze_failure(self, failure: FailureRecord) -> None:
        """Analyze a single failure record"""
        logger.info(f"Analyzing failure for issue #{failure.issue_number}")
        
        # Fetch workflow logs
        if failure.workflow_run_id:
            logs = self.fetch_workflow_logs(failure.workflow_run_id)
            if logs:
                failure.logs = logs
                
                # Use self-healing engine for pattern detection
                if self.healing_engine:
                    try:
                        result = self.healing_engine.diagnose(log_output=logs, run_checks=False)
                        failure.detected_issues = [issue.to_dict() for issue in result.issues]
                        failure.suggested_actions = [action.to_dict() for action in result.suggested_actions]
                        
                        # Determine root cause from detected issues
                        if result.issues:
                            primary_issue = result.issues[0]
                            failure.failure_type = primary_issue.issue_type.value
                            failure.root_cause = primary_issue.description
                            failure.severity = primary_issue.severity.value
                        
                    except Exception as e:
                        logger.warning(f"Self-healing analysis failed: {e}")
                
                # Fallback pattern matching if no self-healing engine
                if not failure.root_cause:
                    failure.root_cause = self._extract_root_cause(logs)
                    failure.failure_type = self._classify_failure_type(logs)
        
        # Fetch issue data for additional context
        issue_data = self.fetch_issue_data(failure.issue_number)
        if issue_data:
            # Extract workflow name from issue title/body
            if not failure.workflow_name:
                title = issue_data.get('title', '')
                # Pattern: "CI Failure: <workflow name>"
                match = re.search(r'CI Failure:\s*(.+?)(?:\s*-|$)', title)
                if match:
                    failure.workflow_name = match.group(1).strip()
    
    def _extract_root_cause(self, logs: str) -> str:
        """Extract root cause from logs using pattern matching"""
        # Common failure patterns
        patterns = [
            (r'FAILED.*?::(\S+)', 'Test failure: {}'),
            (r'ModuleNotFoundError:\s*No module named\s*[\'"](\S+)[\'"]', 'Missing module: {}'),
            (r'AssertionError:\s*(.+)', 'Assertion failed: {}'),
            (r'ImportError:\s*(.+)', 'Import error: {}'),
            (r'SyntaxError:\s*(.+)', 'Syntax error: {}'),
            (r'Error:\s*(.+)', 'Error: {}'),
        ]
        
        for pattern, template in patterns:
            match = re.search(pattern, logs, re.MULTILINE)
            if match:
                return template.format(match.group(1)[:100])
        
        return "Unknown root cause - manual investigation required"
    
    def _classify_failure_type(self, logs: str) -> str:
        """Classify failure type from logs"""
        if re.search(r'FAILED.*test', logs, re.IGNORECASE):
            return 'test_failure'
        elif re.search(r'ModuleNotFoundError|ImportError', logs):
            return 'import_error'
        elif re.search(r'SyntaxError', logs):
            return 'syntax_error'
        elif re.search(r'build.*failed', logs, re.IGNORECASE):
            return 'build_failure'
        elif re.search(r'lint.*error', logs, re.IGNORECASE):
            return 'lint_error'
        else:
            return 'unknown'
    
    def group_failures(self, strategy: str = 'root_cause') -> None:
        """Group failures by specified strategy"""
        logger.info(f"Grouping failures by: {strategy}")
        
        grouped = defaultdict(list)
        
        if strategy == 'root_cause':
            for failure in self.failures:
                key = failure.root_cause or "unknown"
                grouped[key].append(failure)
        
        elif strategy == 'workflow':
            for failure in self.failures:
                key = failure.workflow_name or "unknown_workflow"
                grouped[key].append(failure)
        
        elif strategy == 'severity':
            for failure in self.failures:
                key = failure.severity
                grouped[key].append(failure)
        
        elif strategy == 'failure_type':
            for failure in self.failures:
                key = failure.failure_type or "unknown"
                grouped[key].append(failure)
        
        # Create triage groups
        self.groups = []
        for idx, (key, failures) in enumerate(sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)):
            # Determine group severity (highest severity in group)
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
            
            # Handle empty failures list
            if not failures:
                continue
            
            group_severity = min((f.severity for f in failures), key=lambda s: severity_order.get(s, 10))
            
            # Extract common patterns
            common_patterns = self._extract_common_patterns(failures)
            
            # Generate remediation suggestions
            remediation = self._generate_group_remediations(failures)
            
            group = TriageGroup(
                group_id=f"group_{idx + 1}",
                root_cause=key,
                severity=group_severity,
                failure_count=len(failures),
                failures=failures,
                common_patterns=common_patterns,
                remediation_suggestions=remediation
            )
            self.groups.append(group)
            
            # Update failure records with group info
            issue_nums = [f.issue_number for f in failures]
            for failure in failures:
                failure.grouped_with = [n for n in issue_nums if n != failure.issue_number]
    
    def _extract_common_patterns(self, failures: List[FailureRecord]) -> List[str]:
        """Extract common patterns across failures"""
        patterns = set()
        
        for failure in failures:
            if failure.logs:
                # Extract error messages
                errors = re.findall(r'(Error|Exception|FAILED):\s*(.{20,80})', failure.logs)
                for _, msg in errors:
                    patterns.add(msg.strip())
        
        return sorted(patterns)[:5]  # Top 5 patterns
    
    def _generate_group_remediations(self, failures: List[FailureRecord]) -> List[str]:
        """Generate remediation suggestions for a group"""
        suggestions = []
        
        # Aggregate suggested actions from all failures
        all_actions = []
        for failure in failures:
            all_actions.extend(failure.suggested_actions)
        
        # Deduplicate and prioritize
        seen_types = set()
        for action in all_actions:
            action_type = action.get('action_type', 'unknown')
            if action_type not in seen_types:
                suggestions.append(action.get('description', 'No description'))
                seen_types.add(action_type)
        
        # Add generic suggestions if none found
        if not suggestions:
            suggestions.append("Review logs for common error patterns")
            suggestions.append("Check if issue is reproducible locally")
            suggestions.append("Consider rerunning failed workflows")
        
        return suggestions[:5]  # Top 5 suggestions
    
    def load_from_csv(self, csv_file: Path) -> None:
        """Load failure records from CSV file"""
        logger.info(f"Loading failures from {csv_file}")
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                issue_num = int(row.get('Issue #', row.get('issue_num', 0)))
                if issue_num:
                    failure = FailureRecord(
                        issue_number=issue_num,
                        issue_url=row.get('Issue URL', row.get('issue_url', '')),
                        workflow_run_id=self._extract_run_id(row.get('Failed Workflow Run', row.get('workflow_run', ''))),
                        analysis_run_id=self._extract_run_id(row.get('Self-Healing Analysis Run', row.get('analysis_run', '')))
                    )
                    self.failures.append(failure)
        
        logger.info(f"Loaded {len(self.failures)} failure records")
    
    def load_from_issues(self, issue_numbers: List[int]) -> None:
        """Load failure records from GitHub issues"""
        logger.info(f"Loading failures from {len(issue_numbers)} issues")
        
        for issue_num in issue_numbers:
            issue_data = self.fetch_issue_data(issue_num)
            if issue_data:
                # Extract workflow run IDs from issue body
                body = issue_data.get('body', '')
                workflow_runs = re.findall(r'actions/runs/(\d+)', body)
                
                failure = FailureRecord(
                    issue_number=issue_num,
                    issue_url=f"https://github.com/{self.repo}/issues/{issue_num}",
                    workflow_run_id=workflow_runs[0] if workflow_runs else None,
                    analysis_run_id=workflow_runs[1] if len(workflow_runs) > 1 else None,
                    workflow_name=None
                )
                self.failures.append(failure)
        
        logger.info(f"Loaded {len(self.failures)} failure records")
    
    def _extract_run_id(self, url: str) -> Optional[str]:
        """Extract run ID from GitHub Actions URL"""
        if not url:
            return None
        match = re.search(r'actions/runs/(\d+)', url)
        return match.group(1) if match else None
    
    def generate_markdown_report(self) -> str:
        """Generate markdown triage report"""
        lines = []
        
        # Header
        lines.append("# Batch CI Failure Triage Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append(f"**Repository:** {self.repo}")
        lines.append(f"**Total Failures:** {len(self.failures)}")
        lines.append(f"**Groups Identified:** {len(self.groups)}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        
        severity_counts = defaultdict(int)
        for group in self.groups:
            severity_counts[group.severity] += group.failure_count
        
        lines.append("### Failures by Severity")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                lines.append(f"- {emoji} **{severity.upper()}**: {count} failures")
        lines.append("")
        
        # Grouped Failures
        lines.append("## Grouped Failures")
        lines.append("")
        
        for group in self.groups:
            lines.append(f"### {group.group_id.upper()}: {group.root_cause}")
            lines.append("")
            lines.append(f"**Severity:** {group.severity.upper()} | **Count:** {group.failure_count} failures")
            lines.append("")
            
            # Affected Issues
            lines.append("**Affected Issues:**")
            for failure in group.failures:
                lines.append(f"- #{failure.issue_number} - [Link]({failure.issue_url})")
            lines.append("")
            
            # Common Patterns
            if group.common_patterns:
                lines.append("**Common Patterns:**")
                for pattern in group.common_patterns:
                    lines.append(f"- `{pattern}`")
                lines.append("")
            
            # Remediation Suggestions
            lines.append("**Recommended Actions:**")
            for idx, suggestion in enumerate(group.remediation_suggestions, 1):
                lines.append(f"{idx}. {suggestion}")
            lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Individual Failure Details
        lines.append("## Individual Failure Details")
        lines.append("")
        
        for failure in self.failures:
            lines.append(f"### Issue #{failure.issue_number}")
            lines.append("")
            lines.append(f"- **Issue URL:** {failure.issue_url}")
            lines.append(f"- **Workflow Run:** `{failure.workflow_run_id}`")
            if failure.workflow_name:
                lines.append(f"- **Workflow:** {failure.workflow_name}")
            lines.append(f"- **Failure Type:** {failure.failure_type or 'unknown'}")
            lines.append(f"- **Root Cause:** {failure.root_cause or 'unknown'}")
            lines.append(f"- **Severity:** {failure.severity}")
            
            if failure.grouped_with:
                lines.append(f"- **Grouped With:** #{', #'.join(map(str, failure.grouped_with))}")
            
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Generated by Batch CI Failure Triage Tool*")
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> str:
        """Generate JSON triage report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'repository': self.repo,
            'total_failures': len(self.failures),
            'total_groups': len(self.groups),
            'groups': [group.to_dict() for group in self.groups],
            'failures': [failure.to_dict() for failure in self.failures]
        }
        return json.dumps(report, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Batch triage CI/test failures and generate remediation suggestions'
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--issues', type=str,
                            help='Comma-separated GitHub issue numbers')
    input_group.add_argument('--from-file', type=Path,
                            help='CSV file with issue/workflow data')
    input_group.add_argument('--workflow-runs', type=str,
                            help='Comma-separated workflow run IDs')
    
    # Output options
    parser.add_argument('--output', type=Path, default=Path('batch_triage_report.md'),
                       help='Output file path (default: batch_triage_report.md)')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON instead of markdown')
    
    # Analysis options
    parser.add_argument('--group-by', choices=['root_cause', 'workflow', 'severity', 'failure_type'],
                       default='root_cause',
                       help='Grouping strategy (default: root_cause)')
    parser.add_argument('--repo', default='Aries-Serpent/_codex_',
                       help='GitHub repository (default: Aries-Serpent/_codex_)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize triage engine
    engine = BatchTriageEngine(repo=args.repo)
    
    # Load failures
    if args.issues:
        issue_numbers = [int(n.strip()) for n in args.issues.split(',')]
        engine.load_from_issues(issue_numbers)
    elif args.from_file:
        engine.load_from_csv(args.from_file)
    elif args.workflow_runs:
        # Create failure records from workflow run IDs
        run_ids = [rid.strip() for rid in args.workflow_runs.split(',')]
        for idx, run_id in enumerate(run_ids):
            failure = FailureRecord(
                issue_number=idx + 1,  # Temporary numbering
                issue_url=f"https://github.com/{args.repo}/actions/runs/{run_id}",
                workflow_run_id=run_id
            )
            engine.failures.append(failure)
    
    # Analyze failures
    for failure in engine.failures:
        engine.analyze_failure(failure)
    
    # Group failures
    engine.group_failures(strategy=args.group_by)
    
    # Generate report
    if args.json:
        report = engine.generate_json_report()
        ext = '.json'
        if not args.output.suffix:
            args.output = args.output.with_suffix(ext)
    else:
        report = engine.generate_markdown_report()
        ext = '.md'
        if not args.output.suffix:
            args.output = args.output.with_suffix(ext)
    
    # Write report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding='utf-8')
    
    logger.info(f"✅ Triage report generated: {args.output}")
    logger.info(f"📊 Analyzed {len(engine.failures)} failures in {len(engine.groups)} groups")
    
    # Print summary to console
    print("\n" + "=" * 70)
    print("BATCH TRIAGE SUMMARY")
    print("=" * 70)
    print(f"Total Failures: {len(engine.failures)}")
    print(f"Groups Identified: {len(engine.groups)}")
    print(f"Report: {args.output}")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
