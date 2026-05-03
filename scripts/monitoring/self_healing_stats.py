#!/usr/bin/env python3
"""
Self Healing Stats

Purpose:
    Main execution script

Usage:
    python scripts/monitoring/self_healing_stats.py [options]

    Examples:
    $ python scripts/monitoring/self_healing_stats.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import glob
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import click
import yaml


def load_attempts(lookback_hours: int = None) -> List[Dict]:
    """Load self-healing attempt records"""
    attempts = []
    attempt_files = glob.glob('.codex/self_healing/attempt_*.yaml')

    cutoff_time = None
    if lookback_hours:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    for file_path in attempt_files:
        try:
            with open(file_path) as f:
                attempt = yaml.safe_load(f)

                # Filter by time if specified
                if cutoff_time:
                    attempt_time = datetime.fromisoformat(attempt['timestamp'].replace('Z', '+00:00'))
                    if attempt_time < cutoff_time:
                        continue

                attempts.append(attempt)
        except Exception as e:
            click.echo(f"Warning: Failed to load {file_path}: {e}", err=True)

    return sorted(attempts, key=lambda x: x['timestamp'], reverse=True)


def calculate_overall_stats(attempts: List[Dict]) -> Dict:
    """Calculate overall statistics"""
    if not attempts:
        return {
            'total': 0,
            'successes': 0,
            'failures': 0,
            'success_rate': 0.0
        }

    total = len(attempts)
    successes = sum(1 for a in attempts if a.get('outcome') == 'success')
    failures = total - successes

    return {
        'total': total,
        'successes': successes,
        'failures': failures,
        'success_rate': (successes / total * 100) if total > 0 else 0.0
    }


def calculate_by_fix_type(attempts: List[Dict]) -> Dict:
    """Calculate statistics by fix type"""
    by_type = defaultdict(lambda: {'total': 0, 'success': 0, 'failure': 0})

    for attempt in attempts:
        fix_type = attempt.get('fix_type', 'unknown')
        outcome = attempt.get('outcome', 'failure')

        by_type[fix_type]['total'] += 1
        if outcome == 'success':
            by_type[fix_type]['success'] += 1
        else:
            by_type[fix_type]['failure'] += 1

    # Calculate success rates
    for fix_type in by_type:
        total = by_type[fix_type]['total']
        success = by_type[fix_type]['success']
        by_type[fix_type]['success_rate'] = (success / total * 100) if total > 0 else 0.0

    return dict(by_type)


def format_table(headers: List[str], rows: List[List], col_widths: List[int] = None):
    """Format data as ASCII table"""
    if not col_widths:
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) + 2
                      for i in range(len(headers))]

    # Header
    header_row = ''.join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    separator = ''.join('-' * w for w in col_widths)

    click.echo(header_row)
    click.echo(separator)

    # Rows
    for row in rows:
        click.echo(''.join(f"{cell!s:<{w}}" for cell, w in zip(row, col_widths)))


@click.command()
@click.option('--by-type', is_flag=True, help='Show statistics by fix type')
@click.option('--last', type=int, help='Show last N attempts')
@click.option('--hours', type=int, help='Only show attempts from last N hours')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def main(by_type, last, hours, as_json):
    """Display self-healing CI statistics"""

    # Load attempts
    attempts = load_attempts(lookback_hours=hours)

    if not attempts:
        click.echo("No self-healing attempts found.")
        return

    if last:
        attempts = attempts[:last]

    # Overall stats
    overall = calculate_overall_stats(attempts)

    if as_json:
        import json
        output = {
            'overall': overall,
            'by_fix_type': calculate_by_fix_type(attempts) if by_type else None,
            'recent_attempts': attempts[:last] if last else None
        }
        click.echo(json.dumps(output, indent=2))
        return

    # Display overall statistics
    click.echo("\n" + "=" * 70)
    click.echo("🤖 SELF-HEALING CI STATISTICS")
    click.echo("=" * 70)

    if hours:
        click.echo(f"\n📅 Showing attempts from last {hours} hours")
    elif last:
        click.echo(f"\n📅 Showing last {last} attempts")
    else:
        click.echo("\n📅 Showing all attempts")

    click.echo("\n📊 Overall Statistics:")
    click.echo(f"   Total Attempts:  {overall['total']}")
    click.echo(f"   Successes:       {overall['successes']} ✅")
    click.echo(f"   Failures:        {overall['failures']} ❌")
    click.echo(f"   Success Rate:    {overall['success_rate']:.1f}%")

    # Success rate indicator
    rate = overall['success_rate']
    if rate >= 80:
        indicator = "🟢 Excellent"
    elif rate >= 60:
        indicator = "🟡 Good"
    elif rate >= 40:
        indicator = "🟠 Needs Improvement"
    else:
        indicator = "🔴 Poor"
    click.echo(f"   Rating:          {indicator}")

    # By fix type
    if by_type:
        click.echo("\n📈 Statistics by Fix Type:")
        click.echo()

        by_type_stats = calculate_by_fix_type(attempts)

        headers = ["Fix Type", "Total", "Success", "Failure", "Success Rate"]
        rows = []

        for fix_type, stats in sorted(by_type_stats.items(),
                                       key=lambda x: x[1]['total'],
                                       reverse=True):
            rows.append([
                fix_type,
                stats['total'],
                stats['success'],
                stats['failure'],
                f"{stats['success_rate']:.1f}%"
            ])

        format_table(headers, rows)

    # Recent attempts
    if last:
        click.echo(f"\n📋 Last {min(last, len(attempts))} Attempts:")
        click.echo()

        headers = ["Timestamp", "Fix Type", "Confidence", "Outcome"]
        rows = []

        for attempt in attempts[:last]:
            timestamp = attempt.get('timestamp', 'Unknown')[:19]  # Trim to datetime
            fix_type = attempt.get('fix_type', 'Unknown')
            confidence = f"{attempt.get('confidence', 0)}%"
            outcome = "✅" if attempt.get('outcome') == 'success' else "❌"

            rows.append([timestamp, fix_type, confidence, outcome])

        format_table(headers, rows)

    # Recommendations
    click.echo("\n💡 Recommendations:")
    if overall['success_rate'] < 60:
        click.echo("   - Review failure patterns and refine detection")
        click.echo("   - Consider lowering confidence thresholds")
        click.echo("   - Add more specific fix types")
    elif overall['success_rate'] < 80:
        click.echo("   - System performing well, monitor for improvements")
        click.echo("   - Consider expanding to more CI workflows")
    else:
        click.echo("   - Excellent performance! 🎉")
        click.echo("   - Consider increasing confidence thresholds")
        click.echo("   - Share learnings with other teams")

    click.echo("\n" + "=" * 70)


if __name__ == '__main__':
    main()
