#!/usr/bin/env python3
"""
Configuration Validation Metrics Dashboard

Tracks and visualizes effectiveness of configuration validation across all languages.
Generates HTML dashboard with metrics, charts, and trends.
"""

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class ValidationMetric:
    """Represents a single validation run metric."""
    timestamp: str
    language: str
    status: str  # pass, fail, error
    issues_found: int
    issues_fixed: int
    auto_fix_count: int
    manual_review_count: int
    execution_time_ms: float
    validator_version: str


class MetricsDashboard:
    """Generates metrics dashboard for configuration validation."""

    def __init__(self, metrics_file: Path):
        self.metrics_file = metrics_file
        self.metrics: list[ValidationMetric] = []
        self._load_metrics()

    def _load_metrics(self):
        """Load metrics from JSONL file."""
        if not self.metrics_file.exists():
            return

        with open(self.metrics_file) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    self.metrics.append(ValidationMetric(**data))

    def add_metric(self, metric: ValidationMetric):
        """Add a new metric and persist to file."""
        self.metrics.append(metric)

        # Ensure directory exists
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # Append to JSONL file
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metric)) + '\n')

    def calculate_statistics(self) -> dict[str, Any]:
        """Calculate aggregate statistics."""
        if not self.metrics:
            return {}

        total_runs = len(self.metrics)
        passed = sum(1 for m in self.metrics if m.status == 'pass')
        sum(1 for m in self.metrics if m.status == 'fail')

        total_issues = sum(m.issues_found for m in self.metrics)
        total_fixed = sum(m.issues_fixed for m in self.metrics)
        total_auto_fixed = sum(m.auto_fix_count for m in self.metrics)

        avg_execution_time = sum(m.execution_time_ms for m in self.metrics) / total_runs

        # Per-language stats
        by_language = defaultdict(lambda: {'runs': 0, 'issues': 0, 'fixed': 0})
        for m in self.metrics:
            by_language[m.language]['runs'] += 1
            by_language[m.language]['issues'] += m.issues_found
            by_language[m.language]['fixed'] += m.issues_fixed

        # Recent trend (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent = [m for m in self.metrics
                  if datetime.fromisoformat(m.timestamp) > seven_days_ago]

        return {
            'total_runs': total_runs,
            'success_rate': (passed / total_runs) * 100,
            'total_issues_found': total_issues,
            'total_issues_fixed': total_fixed,
            'fix_rate': (total_fixed / total_issues * 100) if total_issues > 0 else 100,
            'auto_fix_count': total_auto_fixed,
            'auto_fix_rate': (total_auto_fixed / total_fixed * 100) if total_fixed > 0 else 0,
            'avg_execution_time_ms': avg_execution_time,
            'by_language': dict(by_language),
            'recent_7d': {
                'runs': len(recent),
                'issues': sum(m.issues_found for m in recent),
                'fixed': sum(m.issues_fixed for m in recent),
            }
        }

    def generate_html_dashboard(self, output_file: Path):
        """Generate HTML dashboard with charts."""
        stats = self.calculate_statistics()

        if not stats:
            print("⚠️  No metrics data available to generate dashboard")
            return

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Validation Metrics Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .metric-card {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .metric-label {{
            color: #7f8c8d;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            color: #2c3e50;
        }}

        .metric-value.success {{
            color: #27ae60;
        }}

        .metric-value.warning {{
            color: #f39c12;
        }}

        .metric-value.danger {{
            color: #e74c3c;
        }}

        .metric-trend {{
            font-size: 12px;
            color: #27ae60;
            margin-top: 8px;
        }}

        .metric-trend.down {{
            color: #e74c3c;
        }}

        .language-table {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}

        th {{
            color: #7f8c8d;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge.warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .timestamp {{
            color: #95a5a6;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Configuration Validation Metrics</h1>
            <p class="subtitle">Tracking validation effectiveness across all language ecosystems</p>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </header>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value success">{stats['success_rate']:.1f}%</div>
                <div class="metric-trend">↑ Last 7 days: {stats['recent_7d']['runs']} runs</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Issues Found</div>
                <div class="metric-value">{stats['total_issues_found']}</div>
                <div class="metric-trend">Recent: {stats['recent_7d']['issues']} issues</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Fix Rate</div>
                <div class="metric-value success">{stats['fix_rate']:.1f}%</div>
                <div class="metric-trend">{stats['total_issues_fixed']} / {stats['total_issues_found']} fixed</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Auto-Fix Rate</div>
                <div class="metric-value warning">{stats['auto_fix_rate']:.1f}%</div>
                <div class="metric-trend">{stats['auto_fix_count']} automated fixes</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Avg Execution Time</div>
                <div class="metric-value">{stats['avg_execution_time_ms']:.0f}ms</div>
                <div class="metric-trend">Per validation run</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Total Validations</div>
                <div class="metric-value">{stats['total_runs']}</div>
                <div class="metric-trend">Since deployment</div>
            </div>
        </div>

        <div class="language-table">
            <h2 style="margin-bottom: 20px; color: #2c3e50;">Per-Language Statistics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Language</th>
                        <th>Validation Runs</th>
                        <th>Issues Found</th>
                        <th>Issues Fixed</th>
                        <th>Fix Rate</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
'''

        for lang, data in stats['by_language'].items():
            fix_rate = (data['fixed'] / data['issues'] * 100) if data['issues'] > 0 else 100
            status_class = 'success' if fix_rate > 90 else 'warning'
            status_text = '✅ Excellent' if fix_rate > 90 else '⚠️ Needs Attention'

            html += f'''                    <tr>
                        <td><strong>{lang.upper()}</strong></td>
                        <td>{data['runs']}</td>
                        <td>{data['issues']}</td>
                        <td>{data['fixed']}</td>
                        <td>{fix_rate:.1f}%</td>
                        <td><span class="badge {status_class}">{status_text}</span></td>
                    </tr>
'''

        html += '''                </tbody>
            </table>
        </div>

        <div class="language-table">
            <h2 style="margin-bottom: 20px; color: #2c3e50;">Recent Validation History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Language</th>
                        <th>Status</th>
                        <th>Issues</th>
                        <th>Fixed</th>
                        <th>Auto-Fix</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
'''

        # Show last 20 validation runs
        for metric in reversed(self.metrics[-20:]):
            status_class = 'success' if metric.status == 'pass' else 'warning'
            status_icon = '✅' if metric.status == 'pass' else '❌'

            html += f'''                    <tr>
                        <td class="timestamp">{metric.timestamp[:19]}</td>
                        <td>{metric.language.upper()}</td>
                        <td><span class="badge {status_class}">{status_icon} {metric.status.upper()}</span></td>
                        <td>{metric.issues_found}</td>
                        <td>{metric.issues_fixed}</td>
                        <td>{metric.auto_fix_count}</td>
                        <td>{metric.execution_time_ms:.0f}ms</td>
                    </tr>
'''

        html += '''                </tbody>
            </table>
        </div>

        <footer style="text-align: center; margin-top: 40px; color: #95a5a6; font-size: 13px;">
            <p>Configuration Validation Metrics Dashboard v1.0</p>
            <p>Part of the Cognitive Brain CI/CD Prevention System</p>
        </footer>
    </div>
</body>
</html>
'''

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)
        print(f"✅ Dashboard generated: {output_file}")


def main():
    """Generate metrics dashboard."""
    repo_root = Path(__file__).parent.parent.parent
    metrics_file = repo_root / '.codex' / 'metrics' / 'validation_metrics.jsonl'
    output_file = repo_root / '.codex' / 'metrics' / 'dashboard.html'

    dashboard = MetricsDashboard(metrics_file)

    # If no metrics exist, create sample data for demonstration (dev/demo mode only)
    # Set CODEX_DEMO_MODE=1 environment variable to generate sample data
    import os
    if not dashboard.metrics and os.getenv('CODEX_DEMO_MODE'):
        print("📊 Creating sample metrics data for demonstration (DEMO MODE)...")

        # Generate sample metrics
        sample_metrics = [
            ValidationMetric(
                timestamp=datetime.now().isoformat(),
                language="rust",
                status="pass",
                issues_found=0,
                issues_fixed=0,
                auto_fix_count=0,
                manual_review_count=0,
                execution_time_ms=45.2,
                validator_version="1.0"
            ),
            ValidationMetric(
                timestamp=(datetime.now() - timedelta(hours=2)).isoformat(),
                language="python",
                status="pass",
                issues_found=2,
                issues_fixed=2,
                auto_fix_count=2,
                manual_review_count=0,
                execution_time_ms=123.5,
                validator_version="1.0"
            ),
        ]

        for metric in sample_metrics:
            dashboard.add_metric(metric)

    dashboard.generate_html_dashboard(output_file)

    # Print statistics
    stats = dashboard.calculate_statistics()
    print("\n📈 Summary Statistics:")
    print(f"   Total Runs: {stats['total_runs']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print(f"   Issues Found: {stats['total_issues_found']}")
    print(f"   Fix Rate: {stats['fix_rate']:.1f}%")
    print(f"   Auto-Fix Rate: {stats['auto_fix_rate']:.1f}%")


if __name__ == '__main__':
    main()
