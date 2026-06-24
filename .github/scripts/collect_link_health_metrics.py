#!/usr/bin/env python3
"""
Link Health Metrics Collector

Collects link health metrics and maintains historical data for trend analysis.
Generates daily dashboards and alerts on changes.

Author: Link Validator Agent
Date: 2026-06-22
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class LinkHealthMetrics:
    """Collects and manages link health metrics."""

    def __init__(self, metrics_file: Path = None):
        self.metrics_file = metrics_file or Path('.codex/link-health-metrics.json')
        self.history: List[Dict[str, Any]] = []
        self.current: Dict[str, Any] = {}
        self.load_history()

    def load_history(self) -> None:
        """Load historical metrics."""
        if self.metrics_file.exists():
            try:
                data = json.loads(self.metrics_file.read_text())
                self.history = data.get('history', [])
            except Exception as e:
                print(f"Warning: Failed to load metrics file: {e}")
                self.history = []

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current link health metrics."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'link_health': self._run_link_validation(),
            'anchor_health': self._run_anchor_validation(),
            'overall_score': 0
        }

        # Calculate overall score
        link_score = metrics['link_health'].get('health_percentage', 0)
        anchor_score = metrics['anchor_health'].get('health_percentage', 0)
        metrics['overall_score'] = (link_score + anchor_score) / 2

        self.current = metrics
        return metrics

    def _run_link_validation(self) -> Dict[str, Any]:
        """Run link validation and extract metrics."""
        try:
            result = subprocess.run(
                ['python', '.github/scripts/validate-links.py',
                 '--report-file', '/tmp/link_report_metrics.json'],
                capture_output=True,
                text=True,
                timeout=300
            )

            report = json.loads(Path('/tmp/link_report_metrics.json').read_text())

            total = report.get('checked', 0)
            errors = report.get('errors_count', 0)
            valid = total - errors
            health_pct = ((valid / total) * 100) if total > 0 else 0

            return {
                'total_links': total,
                'valid_links': valid,
                'broken_links': errors,
                'health_percentage': round(health_pct, 2),
                'status': 'PASS' if errors == 0 else 'FAIL'
            }
        except Exception as e:
            print(f"Error running link validation: {e}")
            return {
                'total_links': 0,
                'valid_links': 0,
                'broken_links': -1,
                'health_percentage': 0,
                'status': 'ERROR',
                'error': str(e)
            }

    def _run_anchor_validation(self) -> Dict[str, Any]:
        """Run anchor validation and extract metrics."""
        try:
            result = subprocess.run(
                ['python', '.github/scripts/validate_doc_anchors.py',
                 '--directory', 'docs',
                 '--report-file', '/tmp/anchor_report_metrics.json'],
                capture_output=True,
                text=True,
                timeout=300
            )

            report = json.loads(Path('/tmp/anchor_report_metrics.json').read_text())

            stats = report.get('statistics', {})
            errors = stats.get('errors', 0)
            files = stats.get('files_scanned', 0)
            refs = stats.get('cross_references_found', 0)

            valid = refs - errors if refs > 0 else 0
            health_pct = ((valid / refs) * 100) if refs > 0 else 100

            return {
                'files_scanned': files,
                'cross_references': refs,
                'anchor_errors': errors,
                'valid_anchors': valid,
                'health_percentage': round(health_pct, 2),
                'status': 'PASS' if errors == 0 else 'FAIL'
            }
        except Exception as e:
            print(f"Error running anchor validation: {e}")
            return {
                'files_scanned': 0,
                'cross_references': 0,
                'anchor_errors': -1,
                'valid_anchors': 0,
                'health_percentage': 0,
                'status': 'ERROR',
                'error': str(e)
            }

    def save_metrics(self) -> None:
        """Save current metrics to file."""
        self.history.append(self.current)

        # Keep only last 30 days of metrics
        max_history = 30
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]

        data = {
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'current': self.current,
            'history': self.history,
            'trend': self._calculate_trend()
        }

        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_file.write_text(json.dumps(data, indent=2))

    def _calculate_trend(self) -> Dict[str, Any]:
        """Calculate trend metrics."""
        if len(self.history) < 2:
            return {'trend': 'NEUTRAL', 'change': 0}

        current_score = self.history[-1].get('overall_score', 0)
        previous_score = self.history[-2].get('overall_score', 0)
        change = round(current_score - previous_score, 2)

        trend = 'UP' if change > 0 else 'DOWN' if change < 0 else 'NEUTRAL'

        return {
            'trend': trend,
            'change': change,
            'current_score': current_score,
            'previous_score': previous_score
        }

    def print_summary(self) -> None:
        """Print metrics summary."""
        print("\n" + "="*80)
        print("📊 LINK HEALTH METRICS REPORT")
        print("="*80)

        timestamp = self.current.get('timestamp', 'N/A')
        print(f"\nTimestamp: {timestamp}")

        link_health = self.current.get('link_health', {})
        print("\n🔗 Link Health:")
        print(f"   Total links: {link_health.get('total_links', 0)}")
        print(f"   Valid: {link_health.get('valid_links', 0)}")
        print(f"   Broken: {link_health.get('broken_links', 0)}")
        print(f"   Health: {link_health.get('health_percentage', 0)}%")
        print(f"   Status: {link_health.get('status', 'UNKNOWN')}")

        anchor_health = self.current.get('anchor_health', {})
        print("\n⚓ Anchor Health:")
        print(f"   Files scanned: {anchor_health.get('files_scanned', 0)}")
        print(f"   Cross-references: {anchor_health.get('cross_references', 0)}")
        print(f"   Valid: {anchor_health.get('valid_anchors', 0)}")
        print(f"   Errors: {anchor_health.get('anchor_errors', 0)}")
        print(f"   Health: {anchor_health.get('health_percentage', 0)}%")
        print(f"   Status: {anchor_health.get('status', 'UNKNOWN')}")

        overall = self.current.get('overall_score', 0)
        print(f"\n📈 Overall Score: {overall:.2f}/100")

        trend = self._calculate_trend()
        if len(self.history) > 1:
            print(f"   Trend: {trend['trend']} ({trend['change']:+.2f})")

        print("\n" + "="*80 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Collect link health metrics')
    parser.add_argument('--metrics-file', help='Path to metrics file')
    parser.add_argument('--save', action='store_true', help='Save metrics to file')

    args = parser.parse_args()

    collector = LinkHealthMetrics(
        metrics_file=Path(args.metrics_file) if args.metrics_file else None
    )
    collector.collect_metrics()
    collector.print_summary()

    if args.save:
        collector.save_metrics()
        print(f"✅ Metrics saved to {collector.metrics_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
