#!/usr/bin/env python3
"""
Artifact Monitor CLI - Interactive command-line interface for manual monitoring.

This module provides a human-friendly CLI for:
- Running monitoring checks on demand
- Generating failure reports
- Testing pattern matching
- Interactive troubleshooting mode
- Dry-run validation

Usage:
    # Run monitoring check
    python scripts/agents/artifact_monitor_cli.py check

    # Generate report
    python scripts/agents/artifact_monitor_cli.py report --days 7

    # Test pattern matching
    python scripts/agents/artifact_monitor_cli.py test-patterns --log-file path/to/log

    # Interactive mode
    python scripts/agents/artifact_monitor_cli.py interactive

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import yaml

    from scripts.monitoring.agent_orchestrator import AgentOrchestrator
    from scripts.monitoring.artifact_monitor import ArtifactMonitor
    from scripts.monitoring.pattern_analyzer import PatternAnalyzer
except ImportError as e:
    print(f"Error: Failed to import monitoring modules: {e}")
    print("Make sure you're running from the repository root")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ArtifactMonitorCLI:
    """Interactive CLI for artifact monitoring."""

    def __init__(self, config_path: Path, state_path: Path, dry_run: bool = False):
        """
        Initialize CLI.

        Args:
            config_path: Path to monitoring configuration
            state_path: Path to state file
            dry_run: If True, don't create issues or modify state
        """
        self.config_path = config_path
        self.state_path = state_path
        self.dry_run = dry_run

        # Load configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.monitor = ArtifactMonitor(config_path, state_path, dry_run)
        self.pattern_analyzer = PatternAnalyzer(
            Path('.codex/monitoring/patterns/error_signatures.yaml')
        )
        self.agent_orchestrator = AgentOrchestrator(self.config, dry_run)

    def print_header(self, text: str) -> None:
        """Print formatted header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    def print_success(self, text: str) -> None:
        """Print success message."""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

    def print_warning(self, text: str) -> None:
        """Print warning message."""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

    def print_error(self, text: str) -> None:
        """Print error message."""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

    def print_info(self, text: str) -> None:
        """Print info message."""
        print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

    def print_table(self, headers: List[str], rows: List[List[str]]) -> None:
        """Print formatted table."""
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Print header
        header_line = " | ".join(
            f"{h:<{col_widths[i]}}" for i, h in enumerate(headers)
        )
        print(f"{Colors.BOLD}{header_line}{Colors.ENDC}")
        print("-" * len(header_line))

        # Print rows
        for row in rows:
            print(" | ".join(
                f"{cell!s:<{col_widths[i]}}" for i, cell in enumerate(row)
            ))

    def cmd_check(self, workflow: Optional[str] = None) -> int:
        """
        Run monitoring check.

        Args:
            workflow: Specific workflow to check (optional)

        Returns:
            Exit code
        """
        self.print_header("Artifact Monitor - Check")

        if self.dry_run:
            self.print_warning("Running in DRY-RUN mode (no issues will be created)")

        if workflow:
            self.print_info(f"Checking workflow: {workflow}")
            event = self.monitor.check_workflow(workflow)

            if event:
                if event['event'] == 'failure_detected':
                    self.print_error(f"Failure detected in {workflow}")
                    self._print_failure_details(event)
                elif event['event'] == 'recovered':
                    self.print_success(f"Workflow {workflow} has recovered!")
            else:
                self.print_success(f"No issues detected for {workflow}")
        else:
            self.print_info("Checking all monitored workflows...")
            events = self.monitor.check_all_workflows()

            failures = [e for e in events if e['event'] == 'failure_detected']
            recoveries = [e for e in events if e['event'] == 'recovered']

            print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
            print(f"  Total events: {len(events)}")
            self.print_error(f"  Failures: {len(failures)}")
            self.print_success(f"  Recoveries: {len(recoveries)}")

            if failures:
                print(f"\n{Colors.BOLD}Failed Workflows:{Colors.ENDC}")
                for event in failures:
                    self.print_error(f"  - {event['workflow_name']}")

            if recoveries:
                print(f"\n{Colors.BOLD}Recovered Workflows:{Colors.ENDC}")
                for event in recoveries:
                    self.print_success(f"  - {event['workflow_name']}")

        return 0

    def _print_failure_details(self, event: Dict[str, Any]) -> None:
        """Print detailed failure information."""
        metrics = event.get('metrics', {})
        run = event.get('run')

        print(f"\n{Colors.BOLD}Failure Details:{Colors.ENDC}")
        print(f"  Workflow: {event['workflow_name']}")
        print(f"  Run ID: {run.id if run else 'N/A'}")
        print(f"  Consecutive failures: {metrics.get('consecutive_failures', 0)}")
        print(f"  Failure rate: {metrics.get('failure_rate', 0):.1f}%")
        print(f"  Flakiness score: {metrics.get('flakiness_score', 0):.2f}")

    def cmd_report(self, days: int = 7, output: Optional[str] = None) -> int:
        """
        Generate failure report.

        Args:
            days: Number of days to analyze
            output: Output file path (optional)

        Returns:
            Exit code
        """
        self.print_header(f"Artifact Monitor - Report (Last {days} Days)")

        # Load state
        if not self.state_path.exists():
            self.print_error("No state file found. Run 'check' first.")
            return 1

        with open(self.state_path) as f:
            state = json.load(f)

        # Generate report
        stats = state.get('stats', {})
        workflows = state.get('workflows', {})

        # Print statistics
        print(f"\n{Colors.BOLD}Overall Statistics:{Colors.ENDC}")
        self.print_table(
            ['Metric', 'Value'],
            [
                ['Total runs checked', stats.get('total_runs_checked', 0)],
                ['Failures detected', stats.get('failures_detected', 0)],
                ['Patterns matched', stats.get('patterns_matched', 0)],
                ['Issues created', stats.get('issues_created', 0)],
                ['Issues closed', stats.get('issues_closed', 0)],
            ]
        )

        # Print workflow status
        print(f"\n{Colors.BOLD}Workflow Status:{Colors.ENDC}")

        failed_workflows = [
            (name, data) for name, data in workflows.items()
            if data.get('status') == 'failure'
        ]

        if failed_workflows:
            rows = []
            for name, data in failed_workflows:
                rows.append([
                    name,
                    data.get('status', 'unknown'),
                    str(data.get('failure_count', 0)),
                    data.get('last_success', 'Never')[:10] if data.get('last_success') else 'Never'
                ])

            self.print_table(
                ['Workflow', 'Status', 'Failures', 'Last Success'],
                rows
            )
        else:
            self.print_success("No failed workflows!")

        # Save report if output specified
        if output:
            report_data = {
                'generated': datetime.now(timezone.utc).isoformat(),
                'period_days': days,
                'stats': stats,
                'failed_workflows': failed_workflows
            }

            with open(output, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)

            self.print_success(f"Report saved to {output}")

        return 0

    def cmd_test_patterns(
        self,
        log_file: Optional[Path] = None,
        test_string: Optional[str] = None
    ) -> int:
        """
        Test pattern matching.

        Args:
            log_file: Path to log file to analyze
            test_string: Test string to analyze

        Returns:
            Exit code
        """
        self.print_header("Artifact Monitor - Test Patterns")

        # Get log content
        if log_file:
            if not log_file.exists():
                self.print_error(f"Log file not found: {log_file}")
                return 1

            with open(log_file) as f:
                log_content = f.read()

            self.print_info(f"Analyzing log file: {log_file}")
        elif test_string:
            log_content = test_string
            self.print_info("Analyzing test string")
        else:
            self.print_error("Provide --log-file or --test-string")
            return 1

        # Analyze patterns
        matches = self.pattern_analyzer.analyze_logs(log_content)

        if matches:
            self.print_success(f"Found {len(matches)} pattern matches")

            print(f"\n{Colors.BOLD}Pattern Matches:{Colors.ENDC}")
            rows = []
            for match in matches[:10]:  # Show top 10
                rows.append([
                    match.get('name', 'Unknown')[:40],
                    match.get('category', 'unknown'),
                    f"{match.get('confidence', 0) * 100:.0f}%",
                    match.get('severity', 'medium')
                ])

            self.print_table(
                ['Pattern', 'Category', 'Confidence', 'Severity'],
                rows
            )

            # Show recommendations
            if matches:
                category, severity = self.pattern_analyzer.categorize_failure(matches)
                agent = self.pattern_analyzer.get_agent_recommendation(matches)

                print(f"\n{Colors.BOLD}Recommendations:{Colors.ENDC}")
                print(f"  Category: {category}")
                print(f"  Severity: {severity}")
                print(f"  Recommended agent: {agent or 'None'}")
        else:
            self.print_warning("No patterns matched")

        return 0

    def cmd_interactive(self) -> int:
        """
        Interactive troubleshooting mode.

        Returns:
            Exit code
        """
        self.print_header("Artifact Monitor - Interactive Mode")

        print("Commands:")
        print("  check [workflow]  - Check workflows")
        print("  report [days]     - Generate report")
        print("  patterns          - Test patterns")
        print("  state             - Show state")
        print("  help              - Show this help")
        print("  exit              - Exit interactive mode")

        while True:
            try:
                command = input(f"\n{Colors.OKCYAN}monitor>{Colors.ENDC} ").strip()

                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()

                if cmd == 'exit':
                    break
                if cmd == 'help':
                    print("Commands: check, report, patterns, state, help, exit")
                elif cmd == 'check':
                    workflow = parts[1] if len(parts) > 1 else None
                    self.cmd_check(workflow)
                elif cmd == 'report':
                    days = int(parts[1]) if len(parts) > 1 else 7
                    self.cmd_report(days)
                elif cmd == 'patterns':
                    self.print_info("Use: test-patterns --log-file <path>")
                elif cmd == 'state':
                    self._show_state()
                else:
                    self.print_error(f"Unknown command: {cmd}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                self.print_error(f"Error: {e}")

        return 0

    def _show_state(self) -> None:
        """Show current monitoring state."""
        if not self.state_path.exists():
            self.print_warning("No state file found")
            return

        with open(self.state_path) as f:
            state = json.load(f)

        print(f"\n{Colors.BOLD}Monitoring State:{Colors.ENDC}")
        print(f"  Last check: {state.get('last_check_timestamp', 'Never')}")
        print(f"  Tracked workflows: {len(state.get('workflows', {}))}")

        stats = state.get('stats', {})
        print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
        for key, value in stats.items():
            print(f"  {key}: {value}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Artifact Monitor CLI - Interactive monitoring interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run monitoring check
  %(prog)s check

  # Check specific workflow
  %(prog)s check --workflow test-comprehensive.yml

  # Generate 7-day report
  %(prog)s report --days 7

  # Test pattern matching
  %(prog)s test-patterns --log-file logs/workflow.log

  # Interactive mode
  %(prog)s interactive

  # Dry-run mode
  %(prog)s check --dry-run
"""
    )

    # Global options
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
        '--dry-run',
        action='store_true',
        help='Run without creating issues or modifying state'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Check command
    check_parser = subparsers.add_parser('check', help='Run monitoring check')
    check_parser.add_argument(
        '--workflow',
        help='Specific workflow to check'
    )

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate failure report')
    report_parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to analyze (default: 7)'
    )
    report_parser.add_argument(
        '--output',
        type=Path,
        help='Output file path'
    )

    # Test patterns command
    patterns_parser = subparsers.add_parser(
        'test-patterns',
        help='Test pattern matching'
    )
    patterns_parser.add_argument(
        '--log-file',
        type=Path,
        help='Path to log file to analyze'
    )
    patterns_parser.add_argument(
        '--test-string',
        help='Test string to analyze'
    )

    # Interactive command
    subparsers.add_parser('interactive', help='Interactive troubleshooting mode')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    try:
        cli = ArtifactMonitorCLI(args.config, args.state, args.dry_run)
    except Exception as e:
        print(f"Error initializing CLI: {e}")
        return 1

    # Execute command
    try:
        if args.command == 'check':
            return cli.cmd_check(args.workflow)
        if args.command == 'report':
            return cli.cmd_report(args.days, args.output)
        if args.command == 'test-patterns':
            return cli.cmd_test_patterns(args.log_file, args.test_string)
        if args.command == 'interactive':
            return cli.cmd_interactive()
        print(f"Unknown command: {args.command}")
        return 1
    except Exception as e:
        print(f"Error executing command: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
