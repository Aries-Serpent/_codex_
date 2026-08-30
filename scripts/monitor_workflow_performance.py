#!/usr/bin/env python3
"""
Workflow Performance Monitoring Script

Tracks and analyzes GitHub Actions workflow performance metrics including:
- Execution times
- Cache hit rates
- Success rates
- Cost per run
- Comparative analysis (consolidated vs original workflows)

Usage:
    python scripts/monitor_workflow_performance.py [OPTIONS]

Options:
    --days DAYS           Number of days to analyze (default: 14)
    --output PATH         Output path for report (default: .codex/reports/workflow_performance.json)
    --format FORMAT       Output format: json, html, markdown (default: json)
    --compare             Compare consolidated vs original workflows
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
try:
    import requests
    from tabulate import tabulate
except ImportError:
    print("❌ Error: Required packages not installed.")
    print("\nPlease install required packages:")
    print("  pip install requests tabulate")
    print("\nOr install all optional dependencies:")
    print("  pip install -e '.[optional]'")
    sys.exit(1)


class WorkflowMonitor:
    """Monitor and analyze GitHub Actions workflow performance."""

    def __init__(self, repo: str, token: str, days: int = 14, max_pages: int = 10):
        self.repo = repo
        self.token = token
        self.days = days
        self.max_pages = max_pages
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        # nosemgrep: url-substring-check - trusted GitHub API base for workflow monitoring
        self.base_url = f'https://api.github.com/repos/{repo}'

        # Consolidated workflow suites
        self.consolidated_workflows = [
            'Cache Management Suite',
            'Testing Suite',
            'CI/CD Health Suite',
            'Security Scanning Suite',
            'Documentation Suite'
        ]

        # Original workflows that were consolidated
        self.original_workflows = {
            'Cache Management Suite': [
                'cache-warmup.yml',
                'cache-management.yml',
                'cache-cleanup.yml'
            ],
            'Testing Suite': [
                'test-comprehensive.yml',
                'test-rag.yml',
                'auth-tests.yml',
                'coverage_report.yml',
                'determinism.yml',
                'integration-gated.yml'
            ],
            'CI/CD Health Suite': [
                'ci-health-monitor.yml',
                'ci-diagnostic-automation.yml',
                'artifact-monitoring.yml',
                'repository-health-monitoring.yml',
                'runner-diagnostics.yml'
            ],
            'Security Scanning Suite': [
                'codeql-analysis.yml',
                'dependency-scan.yml',
                'security-scan.yml',
                'semgrep_sarif.yml'
            ],
            'Documentation Suite': [
                'pages-mkdocs.yml',
                'api-documentation.yml',
                'wiki-assemble.yml',
                'documentation-link-checker.yml'
            ]
        }

    def fetch_workflow_runs(self, since: Optional[datetime] = None) -> list[dict[str, Any]]:
        """Fetch workflow runs from GitHub API."""
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=self.days)

        url = f'{self.base_url}/actions/runs'
        params = {
            'created': f'>={since.isoformat()}Z',
            'per_page': 100
        }

        all_runs = []
        page = 1

        while True:
            params['page'] = page
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                break

            data = response.json()
            runs = data.get('workflow_runs', [])

            if not runs:
                break

            all_runs.extend(runs)

            # Check if there are more pages
            if len(runs) < 100:
                break

            page += 1

            # Check rate limit to avoid exceeding API limits
            if page > self.max_pages:
                print(f"⚠️  Reached page limit ({self.max_pages}). Use --max-pages to increase.")
                break

        return all_runs

    def calculate_duration(self, run: dict[str, Any]) -> Optional[float]:
        """Calculate workflow run duration in minutes."""
        created = run.get('created_at')
        updated = run.get('updated_at')

        if not created or not updated:
            return None

        try:
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            return (updated_dt - created_dt).total_seconds() / 60
        except Exception:
            return None

    def analyze_workflows(self, runs: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze workflow performance metrics."""
        metrics = defaultdict(lambda: {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'durations': [],
            'avg_duration': 0,
            'p50_duration': 0,
            'p95_duration': 0,
            'success_rate': 0
        })

        for run in runs:
            workflow_name = run.get('name', 'Unknown')
            conclusion = run.get('conclusion', 'unknown')
            status = run.get('status', 'unknown')

            # Skip in-progress runs
            if status != 'completed':
                continue

            duration = self.calculate_duration(run)

            metrics[workflow_name]['total_runs'] += 1

            if conclusion == 'success':
                metrics[workflow_name]['successful_runs'] += 1
            elif conclusion in ['failure', 'timed_out', 'cancelled']:
                metrics[workflow_name]['failed_runs'] += 1

            if duration is not None:
                metrics[workflow_name]['durations'].append(duration)

        # Calculate statistics
        for _, data in metrics.items():
            if data['total_runs'] > 0:
                data['success_rate'] = (data['successful_runs'] / data['total_runs']) * 100

            if data['durations']:
                data['durations'].sort()
                data['avg_duration'] = sum(data['durations']) / len(data['durations'])
                data['p50_duration'] = data['durations'][len(data['durations']) // 2]
                # Safe p95 calculation
                p95_index = min(int(len(data['durations']) * 0.95), len(data['durations']) - 1)
                data['p95_duration'] = data['durations'][p95_index]

        return dict(metrics)

    def compare_consolidated_vs_original(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Compare performance of consolidated vs original workflows."""
        comparisons = {}

        for suite_name, originals in self.original_workflows.items():
            if suite_name not in metrics:
                continue

            suite_metrics = metrics[suite_name]

            # Aggregate original workflow metrics
            original_total_runs = 0
            original_successful = 0
            original_durations = []

            for original_wf in originals:
                for wf_name, wf_metrics in metrics.items():
                    if original_wf in wf_name or wf_name in original_wf:
                        original_total_runs += wf_metrics['total_runs']
                        original_successful += wf_metrics['successful_runs']
                        original_durations.extend(wf_metrics['durations'])

            if original_total_runs == 0:
                continue

            original_avg_duration = sum(original_durations) / len(original_durations) if original_durations else 0
            original_success_rate = (original_successful / original_total_runs) * 100 if original_total_runs > 0 else 0

            # Calculate improvements
            duration_improvement = 0
            if original_avg_duration > 0 and suite_metrics['avg_duration'] > 0:
                duration_improvement = ((original_avg_duration - suite_metrics['avg_duration']) / original_avg_duration) * 100

            success_rate_diff = suite_metrics['success_rate'] - original_success_rate

            comparisons[suite_name] = {
                'consolidated': {
                    'runs': suite_metrics['total_runs'],
                    'avg_duration': suite_metrics['avg_duration'],
                    'success_rate': suite_metrics['success_rate']
                },
                'original': {
                    'runs': original_total_runs,
                    'avg_duration': original_avg_duration,
                    'success_rate': original_success_rate
                },
                'improvement': {
                    'duration_percent': duration_improvement,
                    'success_rate_diff': success_rate_diff
                }
            }

        return comparisons

    def generate_report(self, metrics: dict[str, Any], comparisons: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'analysis_period_days': self.days,
            'repository': self.repo,
            'consolidated_workflows': {},
            'all_workflows': metrics,
            'summary': {
                'total_workflows': len(metrics),
                'total_runs': sum(m['total_runs'] for m in metrics.values()),
                'avg_success_rate': sum(m['success_rate'] for m in metrics.values()) / len(metrics) if metrics else 0
            }
        }

        # Extract consolidated workflow metrics
        for wf_name in self.consolidated_workflows:
            if wf_name in metrics:
                report['consolidated_workflows'][wf_name] = metrics[wf_name]

        if comparisons:
            report['comparisons'] = comparisons

            # Calculate overall improvement
            if comparisons:
                avg_duration_improvement = sum(c['improvement']['duration_percent'] for c in comparisons.values()) / len(comparisons)
                report['summary']['avg_duration_improvement'] = avg_duration_improvement

        return report

    def format_markdown(self, report: dict[str, Any]) -> str:
        """Format report as Markdown."""
        md = f"""# Workflow Performance Report

**Generated:** {report['generated_at']}
**Analysis Period:** {report['analysis_period_days']} days
**Repository:** {report['repository']}

## Summary

- **Total Workflows:** {report['summary']['total_workflows']}
- **Total Runs:** {report['summary']['total_runs']}
- **Average Success Rate:** {report['summary']['avg_success_rate']:.2f}%
"""

        if 'avg_duration_improvement' in report['summary']:
            md += f"- **Average Duration Improvement:** {report['summary']['avg_duration_improvement']:.2f}%\n"

        md += "\n## Consolidated Workflow Performance\n\n"

        table_data = []
        for wf_name, metrics in report['consolidated_workflows'].items():
            table_data.append([
                wf_name,
                metrics['total_runs'],
                f"{metrics['avg_duration']:.2f}m",
                f"{metrics['p50_duration']:.2f}m",
                f"{metrics['p95_duration']:.2f}m",
                f"{metrics['success_rate']:.2f}%"
            ])

        md += tabulate(
            table_data,
            headers=['Workflow', 'Runs', 'Avg Time', 'P50', 'P95', 'Success Rate'],
            tablefmt='github'
        )

        if 'comparisons' in report:
            md += "\n\n## Consolidated vs Original Comparison\n\n"

            comp_data = []
            for suite_name, comp in report['comparisons'].items():
                comp_data.append([
                    suite_name,
                    f"{comp['consolidated']['avg_duration']:.2f}m",
                    f"{comp['original']['avg_duration']:.2f}m",
                    f"{comp['improvement']['duration_percent']:+.2f}%",
                    f"{comp['consolidated']['success_rate']:.2f}%",
                    f"{comp['original']['success_rate']:.2f}%"
                ])

            md += tabulate(
                comp_data,
                headers=['Suite', 'New Time', 'Old Time', 'Improvement', 'New Success', 'Old Success'],
                tablefmt='github'
            )

        return md

    def run(self, output_path: Path, output_format: str = 'json', compare: bool = False) -> None:
        """Run the monitoring analysis."""
        print(f"📊 Fetching workflow runs for the last {self.days} days...")
        runs = self.fetch_workflow_runs()
        print(f"✅ Fetched {len(runs)} workflow runs")

        print("📈 Analyzing workflow performance...")
        metrics = self.analyze_workflows(runs)
        print(f"✅ Analyzed {len(metrics)} workflows")

        comparisons = None
        if compare:
            print("🔄 Comparing consolidated vs original workflows...")
            comparisons = self.compare_consolidated_vs_original(metrics)
            print(f"✅ Generated {len(comparisons)} comparisons")

        print("📝 Generating report...")
        report = self.generate_report(metrics, comparisons)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report saved to: {output_path}")

        elif output_format == 'markdown':
            md_path = output_path.with_suffix('.md')
            md_content = self.format_markdown(report)
            with open(md_path, 'w') as f:
                f.write(md_content)
            print(f"✅ Report saved to: {md_path}")

        elif output_format == 'html':
            print("⚠️  HTML format not yet implemented")

        # Print summary to console
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total Workflows: {report['summary']['total_workflows']}")
        print(f"Total Runs: {report['summary']['total_runs']}")
        print(f"Average Success Rate: {report['summary']['avg_success_rate']:.2f}%")

        if 'avg_duration_improvement' in report['summary']:
            print(f"Average Duration Improvement: {report['summary']['avg_duration_improvement']:.2f}%")

        print("\nTop 5 Most Active Workflows:")
        sorted_workflows = sorted(
            metrics.items(),
            key=lambda x: x[1]['total_runs'],
            reverse=True
        )[:5]

        for i, (wf_name, wf_metrics) in enumerate(sorted_workflows, 1):
            print(f"{i}. {wf_name}: {wf_metrics['total_runs']} runs, {wf_metrics['success_rate']:.2f}% success")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Monitor GitHub Actions workflow performance'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=14,
        help='Number of days to analyze (default: 14)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum API pages to fetch (default: 10, 100 runs per page)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(REPO_ROOT / '.codex' / 'reports' / 'workflow_performance.json'),
        help='Output path for report'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'html', 'markdown'],
        default='json',
        help='Output format'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare consolidated vs original workflows'
    )
    parser.add_argument(
        '--repo',
        default=os.environ.get('GITHUB_REPOSITORY', 'Aries-Serpent/_codex_'),
        help='GitHub repository (default: from GITHUB_REPOSITORY env)'
    )
    parser.add_argument(
        '--token',
        default=os.environ.get('GITHUB_TOKEN', ''),
        help='GitHub token (default: from GITHUB_TOKEN env)'
    )

    args = parser.parse_args()

    if not args.token:
        print("❌ Error: GitHub token required. Set GITHUB_TOKEN env or use --token")
        sys.exit(1)

    monitor = WorkflowMonitor(args.repo, args.token, args.days, args.max_pages)
    monitor.run(args.output, args.format, args.compare)


if __name__ == '__main__':
    main()
