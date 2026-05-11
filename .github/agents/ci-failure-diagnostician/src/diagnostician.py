#!/usr/bin/env python3
"""
CI Failure Diagnostician

Deep-dive analysis of complex CI failures that cannot be automatically fixed.
Provides root cause analysis, dependency conflict detection, and actionable recommendations.
"""

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
import yaml


@dataclass
class DiagnosticReport:
    """Comprehensive diagnostic report"""
    timestamp: str
    workflow_run_id: str
    root_cause: dict
    evidence: list[str]
    manual_steps: list[str]
    similar_past_failures: list[dict]
    estimated_fix_time: str
    confidence: int


class CIFailureDiagnostician:
    """Analyzes complex CI failures and provides detailed diagnostics"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize diagnostician"""
        self.config = self._load_config(config_path)
        self.cognitive_brain_path = Path('.codex/self_healing')

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load configuration"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {
            'max_log_lines': 10000,
            'context_lines': 20,
            'min_confidence': 60,
            'cognitive_brain_enabled': True
        }

    def diagnose(self, workflow_run_id: str, logs: str) -> DiagnosticReport:
        """
        Perform comprehensive diagnostic analysis

        Args:
            workflow_run_id: GitHub Actions workflow run ID
            logs: Full failure logs

        Returns:
            DiagnosticReport with findings
        """
        # Extract key information
        error_patterns = self._extract_error_patterns(logs)
        stack_traces = self._extract_stack_traces(logs)
        dependency_info = self._analyze_dependencies(logs)

        # Determine root cause
        root_cause, confidence = self._determine_root_cause(
            error_patterns,
            stack_traces,
            dependency_info
        )

        # Build evidence chain
        evidence = self._build_evidence_chain(
            error_patterns,
            stack_traces,
            root_cause
        )

        # Generate manual fix steps
        manual_steps = self._generate_manual_steps(root_cause, evidence)

        # Query cognitive brain for similar failures
        similar_failures = self._query_similar_failures(root_cause)

        # Estimate fix time
        fix_time = self._estimate_fix_time(root_cause, similar_failures)

        return DiagnosticReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_run_id=workflow_run_id,
            root_cause=root_cause,
            evidence=evidence,
            manual_steps=manual_steps,
            similar_past_failures=similar_failures,
            estimated_fix_time=fix_time,
            confidence=confidence
        )

    def _extract_error_patterns(self, logs: str) -> list[dict]:
        """Extract error patterns from logs"""
        patterns = []
        error_regex = [
            (r'error: (.+)', 'generic_error'),
            (r'Error: (.+)', 'error_message'),
            (r'FAILED (.+)', 'test_failure'),
            (r'(\w+Error): (.+)', 'python_exception'),
            (r'panicked at (.+)', 'rust_panic'),
        ]

        for line_num, line in enumerate(logs.split('\n'), 1):
            for regex, pattern_type in error_regex:
                match = re.search(regex, line)
                if match:
                    patterns.append({
                        'type': pattern_type,
                        'line': line_num,
                        'message': match.group(0),
                        'details': match.groups()
                    })

        return patterns

    def _extract_stack_traces(self, logs: str) -> list[dict]:
        """Extract stack traces from logs"""
        traces = []
        lines = logs.split('\n')

        # Look for Python stack traces
        for i, line in enumerate(lines):
            if 'Traceback (most recent call last):' in line:
                trace_lines = []
                j = i + 1
                while j < len(lines) and (lines[j].startswith('  ') or 'Error:' in lines[j]):
                    trace_lines.append(lines[j])
                    j += 1
                if trace_lines:
                    traces.append({
                        'type': 'python',
                        'start_line': i + 1,
                        'trace': '\n'.join(trace_lines),
                        'length': len(trace_lines)
                    })

        return traces

    def _analyze_dependencies(self, logs: str) -> dict:
        """Analyze dependency-related issues"""
        dep_issues = {
            'version_conflicts': [],
            'missing_packages': [],
            'incompatibilities': []
        }

        # Check for version conflicts
        conflict_patterns = [
            r'conflicting versions for (\w+)',
            r'(\w+) .+ is incompatible with',
            r'requires (\w+) .+ but',
        ]

        for pattern in conflict_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            dep_issues['version_conflicts'].extend(matches)

        # Check for missing packages
        missing_patterns = [
            r"No module named '([^']+)'",
            r'cannot find (\w+) in the registry',
            r'(\w+): command not found',
        ]

        for pattern in missing_patterns:
            matches = re.findall(pattern, logs)
            dep_issues['missing_packages'].extend(matches)

        return dep_issues

    def _determine_root_cause(
        self,
        error_patterns: list[dict],
        stack_traces: list[dict],
        dependency_info: dict
    ) -> tuple[dict, int]:
        """Determine the root cause of the failure"""

        # Check for dependency issues first (often root cause)
        if dependency_info['version_conflicts']:
            return {
                'type': 'dependency_conflict',
                'description': f"Version conflict: {', '.join(set(dependency_info['version_conflicts'][:3]))}",
                'category': 'dependencies',
                'automated_fix': False
            }, 85

        if dependency_info['missing_packages']:
            missing = list(set(dependency_info['missing_packages']))[:3]
            return {
                'type': 'missing_dependency',
                'description': f"Missing packages: {', '.join(missing)}",
                'category': 'dependencies',
                'automated_fix': True  # Can be fixed by add_dependency
            }, 90

        # Check stack traces for runtime errors
        if stack_traces:
            trace = stack_traces[0]
            return {
                'type': 'runtime_error',
                'description': f"Runtime error in {trace['type']} code",
                'category': 'code_logic',
                'automated_fix': False
            }, 70

        # Check error patterns
        if error_patterns:
            first_error = error_patterns[0]
            return {
                'type': first_error['type'],
                'description': first_error['message'][:100],
                'category': 'build_error',
                'automated_fix': False
            }, 65

        # Unknown failure
        return {
            'type': 'unknown',
            'description': 'Unable to determine root cause from logs',
            'category': 'unknown',
            'automated_fix': False
        }, 0

    def _build_evidence_chain(
        self,
        error_patterns: list[dict],
        stack_traces: list[dict],
        root_cause: dict
    ) -> list[str]:
        """Build evidence chain supporting the root cause"""
        evidence = []

        if error_patterns:
            evidence.append(f"Found {len(error_patterns)} error message(s) in logs")
            for pattern in error_patterns[:3]:
                evidence.append(f"Line {pattern['line']}: {pattern['message'][:80]}")

        if stack_traces:
            evidence.append(f"Found {len(stack_traces)} stack trace(s)")
            for trace in stack_traces[:2]:
                evidence.append(f"Stack trace starting at line {trace['start_line']} ({trace['length']} lines)")

        return evidence

    def _generate_manual_steps(self, root_cause: dict, evidence: list[str]) -> list[str]:
        """Generate manual fix steps based on root cause"""
        steps = []

        if root_cause['type'] == 'dependency_conflict':
            steps = [
                "Review Cargo.lock or package-lock.json for conflicts",
                "Run `cargo update` or `npm update` to resolve",
                "Check for breaking changes in dependency changelog",
                "Test locally before pushing"
            ]
        elif root_cause['type'] == 'missing_dependency':
            steps = [
                "Add missing package to requirements.txt or Cargo.toml",
                "Run package manager to install",
                "Verify import/usage in code",
                "Test locally"
            ]
        elif root_cause['type'] == 'runtime_error':
            steps = [
                "Review stack trace for error location",
                "Check for recent code changes in affected area",
                "Verify input data and assumptions",
                "Add error handling if needed",
                "Test with debugger locally"
            ]
        else:
            steps = [
                "Review full logs for additional context",
                "Search for similar issues in repository history",
                "Check recent commits for related changes",
                "Consult team if issue persists"
            ]

        return steps

    def _query_similar_failures(self, root_cause: dict) -> list[dict]:
        """Query cognitive brain for similar past failures"""
        similar = []

        if not self.config.get('cognitive_brain_enabled'):
            return similar

        if not self.cognitive_brain_path.exists():
            return similar

        # Load past attempts
        for attempt_file in self.cognitive_brain_path.glob('attempt_*.yaml'):
            try:
                with open(attempt_file) as f:
                    attempt = yaml.safe_load(f)

                # Check if failure types match
                if attempt.get('fix_type') == root_cause.get('type'):
                    similar.append({
                        'date': attempt.get('timestamp'),
                        'fix_type': attempt.get('fix_type'),
                        'outcome': attempt.get('outcome'),
                        'confidence': attempt.get('confidence')
                    })
            except Exception:
                continue

        return similar[:5]  # Return top 5

    def _estimate_fix_time(self, root_cause: dict, similar_failures: list[dict]) -> str:
        """Estimate time to fix based on root cause and history"""
        # Calculate average from similar failures
        if similar_failures:
            # If we've seen this before and fixed it, likely quick
            successful = [f for f in similar_failures if f['outcome'] == 'success']
            if successful:
                return "10-15 minutes (similar issue fixed before)"

        # Estimate based on root cause type
        time_estimates = {
            'dependency_conflict': "20-30 minutes",
            'missing_dependency': "5-10 minutes",
            'runtime_error': "30-60 minutes",
            'build_error': "15-30 minutes",
            'unknown': "60+ minutes (requires investigation)"
        }

        return time_estimates.get(root_cause['type'], "30-45 minutes")

    def generate_report_markdown(self, report: DiagnosticReport) -> str:
        """Generate markdown report"""
        md = f"""# CI Failure Diagnostic Report

**Workflow Run**: {report.workflow_run_id}
**Timestamp**: {report.timestamp}
**Confidence**: {report.confidence}%

## Root Cause

**Type**: `{report.root_cause['type']}`
**Category**: {report.root_cause['category']}
**Description**: {report.root_cause['description']}
**Automated Fix Available**: {'Yes ✅' if report.root_cause.get('automated_fix') else 'No ❌'}

## Evidence

"""
        for i, evidence in enumerate(report.evidence, 1):
            md += f"{i}. {evidence}\n"

        md += "\n## Manual Fix Steps\n\n"
        for i, step in enumerate(report.manual_steps, 1):
            md += f"{i}. {step}\n"

        if report.similar_past_failures:
            md += "\n## Similar Past Failures\n\n"
            md += "| Date | Fix Type | Outcome |\n"
            md += "|------|----------|----------|\n"
            for failure in report.similar_past_failures:
                outcome_icon = "✅" if failure['outcome'] == 'success' else "❌"
                md += f"| {failure['date'][:19]} | {failure['fix_type']} | {outcome_icon} {failure['outcome']} |\n"

        md += f"\n## Estimated Fix Time\n\n{report.estimated_fix_time}\n"

        md += "\n---\n*Generated by CI Failure Diagnostician Agent*\n"

        return md


@click.command()
@click.option('--run-id', required=True, help='Workflow run ID')
@click.option('--log-file', type=click.Path(exists=True), help='Path to log file (if not using gh CLI)')
@click.option('--output', type=click.Path(), default='diagnostic_report.md', help='Output file path')
@click.option('--config', type=click.Path(exists=True), help='Config file path')
def main(run_id, log_file, output, config):
    """Run CI failure diagnostics"""

    diagnostician = CIFailureDiagnostician(
        config_path=Path(config) if config else None
    )

    # Get logs
    if log_file:
        logs = Path(log_file).read_text()
    else:
        # Try to download using gh CLI
        try:
            result = subprocess.run(
                ['gh', 'run', 'view', run_id, '--log'],
                capture_output=True,
                text=True,
                check=True
            )
            logs = result.stdout
        except subprocess.CalledProcessError as e:
            click.echo(f"Error downloading logs: {e}", err=True)
            click.echo("Provide --log-file if gh CLI is not available", err=True)
            return 1

    # Perform diagnosis
    click.echo(f"Analyzing failure for run {run_id}...")
    report = diagnostician.diagnose(run_id, logs)

    # Generate and save report
    markdown = diagnostician.generate_report_markdown(report)
    Path(output).write_text(markdown)

    click.echo(f"\n✅ Diagnostic report saved to: {output}")
    click.echo(f"\nRoot Cause: {report.root_cause['description']}")
    click.echo(f"Confidence: {report.confidence}%")
    click.echo(f"Estimated Fix Time: {report.estimated_fix_time}")
    return 0


if __name__ == '__main__':
    main()
