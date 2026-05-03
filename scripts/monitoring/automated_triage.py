#!/usr/bin/env python3
"""
Automated Workflow Failure Triage Tool
Analyzes workflow failures and provides automated diagnosis and recommendations.

Usage:
    python scripts/monitoring/automated_triage.py --run-id 21681398972
    python scripts/monitoring/automated_triage.py --workflow-name "Testing Suite"
    python scripts/monitoring/automated_triage.py --auto  # Auto-detect failures
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class FailurePattern:
    """Represents a known failure pattern with detection and remediation."""

    def __init__(self, name: str, description: str, detection_patterns: list[str],
                 root_cause: str, solution: str, risk_level: str = "MEDIUM"):
        self.name = name
        self.description = description
        self.detection_patterns = detection_patterns
        self.root_cause = root_cause
        self.solution = solution
        self.risk_level = risk_level

    def matches(self, logs: str) -> bool:
        """Check if logs match this failure pattern."""
        for pattern in self.detection_patterns:
            if re.search(pattern, logs, re.IGNORECASE | re.MULTILINE):
                return True
        return False


# Known failure patterns database
FAILURE_PATTERNS = [
    FailurePattern(
        name="Coverage Artifact Missing",
        description="Coverage XML file not generated before upload",
        detection_patterns=[
            r"coverage.*xml.*missing",
            r"creating placeholder.*coverage",
            r"No such file or directory.*coverage\.xml"
        ],
        root_cause="Tests running without --cov flag or coverage not properly configured",
        solution="Add validation step before artifact upload:\n"
                 "if [ ! -f coverage.xml ]; then\n"
                 "  echo 'ERROR: coverage.xml not generated'\n"
                 "  exit 1\n"
                 "fi",
        risk_level="HIGH"
    ),
    FailurePattern(
        name="Test Summary Logic Error",
        description="Hardcoded status string instead of job outcome evaluation",
        detection_patterns=[
            r'if.*\[\[.*"failure".*==.*"failure"',
            r'❌ Tests failed.*exit 1',
            r'Test Summary.*failure.*failure'
        ],
        root_cause="Workflow using string literal comparison instead of needs.<job>.result",
        solution="Replace hardcoded check with proper evaluation:\n"
                 "if [[ \"${{ needs.core-tests.result }}\" == \"failure\" ]]; then\n"
                 "  exit 1\n"
                 "fi",
        risk_level="HIGH"
    ),
    FailurePattern(
        name="Import Error",
        description="Python module import failure",
        detection_patterns=[
            r"ModuleNotFoundError:",
            r"ImportError:",
            r"No module named"
        ],
        root_cause="Missing dependency or incorrect Python path",
        solution="Check pyproject.toml dependencies and PYTHONPATH configuration",
        risk_level="MEDIUM"
    ),
    FailurePattern(
        name="Permission Denied",
        description="File or directory permission issue",
        detection_patterns=[
            r"Permission denied",
            r"EACCES:",
            r"Operation not permitted"
        ],
        root_cause="Insufficient file system permissions",
        solution="Add chmod step before operation or check file ownership",
        risk_level="LOW"
    ),
    FailurePattern(
        name="Timeout",
        description="Job exceeded time limit",
        detection_patterns=[
            r"The operation was canceled",
            r"timeout",
            r"exceeded.*time limit"
        ],
        root_cause="Job running longer than timeout setting",
        solution="Increase timeout-minutes setting or optimize job performance",
        risk_level="MEDIUM"
    ),
    FailurePattern(
        name="Out of Memory",
        description="Job ran out of available memory",
        detection_patterns=[
            r"Out of memory",
            r"OOMKilled",
            r"MemoryError",
            r"Cannot allocate memory"
        ],
        root_cause="Job memory usage exceeds available resources",
        solution="Reduce batch size, optimize memory usage, or use larger runner",
        risk_level="HIGH"
    ),
    FailurePattern(
        name="Disk Space Full",
        description="Insufficient disk space",
        detection_patterns=[
            r"No space left on device",
            r"ENOSPC:",
            r"disk.*full"
        ],
        root_cause="Runner out of disk space",
        solution="Clean up artifacts, cache, or use larger runner",
        risk_level="HIGH"
    ),
    FailurePattern(
        name="Network Error",
        description="Network connectivity or download failure",
        detection_patterns=[
            r"Failed to connect",
            r"Connection refused",
            r"Could not resolve host",
            r"curl.*failed"
        ],
        root_cause="Network connectivity issue or remote service unavailable",
        solution="Add retry logic or check service status",
        risk_level="LOW"
    ),
]


class WorkflowTriageAnalyzer:
    """Automated workflow failure triage and diagnosis."""

    def __init__(self):
        self.patterns = FAILURE_PATTERNS

    def analyze_failure(self, run_id: str, workflow_name: str,
                       logs: Optional[str] = None) -> dict:
        """Analyze a workflow failure and provide diagnosis."""
        analysis = {
            'run_id': run_id,
            'workflow_name': workflow_name,
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
            'matched_patterns': [],
            'recommendations': [],
            'risk_level': 'UNKNOWN',
        }

        if logs is None:
            analysis['status'] = 'NO_LOGS_PROVIDED'
            analysis['recommendations'].append(
                "Provide logs for detailed analysis using GitHub API"
            )
            return analysis

        # Check each pattern
        matched_any = False
        max_risk = "LOW"
        for pattern in self.patterns:
            if pattern.matches(logs):
                matched_any = True
                analysis['matched_patterns'].append({
                    'name': pattern.name,
                    'description': pattern.description,
                    'root_cause': pattern.root_cause,
                    'solution': pattern.solution,
                    'risk_level': pattern.risk_level,
                })

                # Track highest risk level
                if pattern.risk_level == "HIGH":
                    max_risk = "HIGH"
                elif pattern.risk_level == "MEDIUM" and max_risk != "HIGH":
                    max_risk = "MEDIUM"

        analysis['risk_level'] = max_risk

        if not matched_any:
            analysis['status'] = 'NO_KNOWN_PATTERN'
            analysis['recommendations'].append(
                "Manual investigation required - no known pattern matched"
            )
            analysis['recommendations'].append(
                "Review full logs and consider adding new pattern to database"
            )
        else:
            analysis['status'] = 'PATTERNS_MATCHED'
            analysis['recommendations'].append(
                f"Found {len(analysis['matched_patterns'])} known failure pattern(s)"
            )
            analysis['recommendations'].append(
                "Review matched patterns and apply suggested solutions"
            )

        return analysis

    def generate_report(self, analysis: dict) -> str:
        """Generate human-readable triage report."""
        lines = []
        lines.append("=" * 80)
        lines.append("AUTOMATED WORKFLOW FAILURE TRIAGE REPORT")
        lines.append("=" * 80)
        lines.append(f"Workflow: {analysis['workflow_name']}")
        lines.append(f"Run ID: {analysis['run_id']}")
        lines.append(f"Analyzed: {analysis['analyzed_at']}")
        lines.append(f"Status: {analysis['status']}")
        lines.append(f"Risk Level: {analysis['risk_level']}")
        lines.append("-" * 80)

        if analysis['matched_patterns']:
            lines.append("\nMATCHED FAILURE PATTERNS:")
            for i, pattern in enumerate(analysis['matched_patterns'], 1):
                lines.append(f"\n{i}. {pattern['name']} [{pattern['risk_level']}]")
                lines.append(f"   Description: {pattern['description']}")
                lines.append(f"   Root Cause: {pattern['root_cause']}")
                lines.append("   Solution:")
                for line in pattern['solution'].split('\n'):
                    lines.append(f"      {line}")

        lines.append("\nRECOMMENDATIONS:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            lines.append(f"{i}. {rec}")

        lines.append("\n" + "=" * 80)
        return '\n'.join(lines)

    def batch_analyze(self, workflow_runs: list[dict]) -> list[dict]:
        """Analyze multiple workflow runs."""
        results = []
        for run in workflow_runs:
            analysis = self.analyze_failure(
                run.get('id', 'unknown'),
                run.get('name', 'unknown'),
                run.get('logs', None)
            )
            results.append(analysis)
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Automated workflow failure triage and diagnosis'
    )
    parser.add_argument(
        '--run-id',
        help='Workflow run ID to analyze'
    )
    parser.add_argument(
        '--workflow-name',
        help='Workflow name'
    )
    parser.add_argument(
        '--logs-file',
        help='Path to log file for analysis'
    )
    parser.add_argument(
        '--output',
        default='triage_report.txt',
        help='Output report file (default: triage_report.txt)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON format instead of text'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-detect failures from active_workflow_status.json'
    )

    args = parser.parse_args()

    analyzer = WorkflowTriageAnalyzer()

    if args.auto:
        # Auto-detect from status file
        status_file = Path('.codex/active_workflow_status.json')
        if not status_file.exists():
            print(f"Error: {status_file} not found. Run parse_active_workflows.py first.")
            sys.exit(1)

        with open(status_file) as f:
            data = json.load(f)

        failed_workflows = [w for w in data.get('workflows', []) if w['status'] == 'FAILING']
        if not failed_workflows:
            print("No failing workflows detected.")
            sys.exit(0)

        print(f"Found {len(failed_workflows)} failing workflow(s). Analyzing...")
        results = analyzer.batch_analyze(failed_workflows)

        for analysis in results:
            report = analyzer.generate_report(analysis)
            print(report)
            print()

    elif args.run_id and args.workflow_name:
        # Analyze specific workflow
        logs = None
        if args.logs_file:
            logs_path = Path(args.logs_file)
            if logs_path.exists():
                with open(logs_path) as f:
                    logs = f.read()

        analysis = analyzer.analyze_failure(args.run_id, args.workflow_name, logs)

        output = json.dumps(analysis, indent=2) if args.json else analyzer.generate_report(analysis)

        # Write to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(output)

        print(f"Triage report written to: {output_path}")

        # Also print to stdout
        print("\n" + output)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
