#!/usr/bin/env python3
"""
Analyze CodeQL Alert Distribution

Processes alert inventory to provide statistical analysis,
pattern detection, and prioritization recommendations.

Author: AI Agent (Phase 34)
Created: 2026-01-26
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def load_alert_inventory(file_path: Path) -> Dict[str, Any]:
    """Load alert inventory from JSON file."""
    with open(file_path) as f:
        return json.load(f)

def analyze_by_severity(alerts: List[Dict]) -> Dict[str, int]:
    """Count alerts by severity level."""
    severity_counts = Counter(alert['severity'] for alert in alerts)
    return dict(severity_counts)

def analyze_by_category(alerts: List[Dict]) -> Dict[str, int]:
    """Count alerts by vulnerability category."""
    category_counts = Counter(alert['category'] for alert in alerts)
    return dict(category_counts)

def analyze_by_file(alerts: List[Dict]) -> List[tuple]:
    """Find files with most alerts."""
    file_counts = Counter(alert['file_path'] for alert in alerts)
    return file_counts.most_common(20)

def analyze_by_cwe(alerts: List[Dict]) -> Dict[str, int]:
    """Count alerts by CWE identifier."""
    cwe_counts = Counter(
        alert.get('cwe_id', 'Unknown') for alert in alerts
    )
    return dict(cwe_counts)

def prioritize_alerts(alerts: List[Dict]) -> Dict[str, List[Dict]]:
    """Prioritize alerts by P0-P4 matrix."""
    priority_map = {
        'P0': [],
        'P1': [],
        'P2': [],
        'P3': [],
        'P4': []
    }

    for alert in alerts:
        severity = alert['severity']

        # Apply priority matrix from planset
        if severity == 'critical':
            priority_map['P0'].append(alert)
        elif severity == 'high':
            priority_map['P1'].append(alert)
        elif severity == 'medium':
            priority_map['P2'].append(alert)
        elif severity == 'low':
            priority_map['P3'].append(alert)
        else:
            # Reserve P4 for informational or unexpected severities
            priority_map['P4'].append(alert)

    return priority_map

def generate_report(inventory: Dict[str, Any], output_path: Path) -> None:
    """Generate comprehensive analysis report."""
    alerts = inventory.get('alerts', [])
    total = len(alerts)

    if total == 0:
        print("No alerts to analyze")
        return

    # Perform analyses
    by_severity = analyze_by_severity(alerts)
    by_category = analyze_by_category(alerts)
    by_file = analyze_by_file(alerts)
    by_cwe = analyze_by_cwe(alerts)
    priorities = prioritize_alerts(alerts)

    # Generate markdown report
    lines = [
        "# CodeQL Alert Analysis Report",
        "",
        f"**Generated:** {inventory.get('exported_at', 'Unknown')}",
        f"**Total Alerts:** {total}",
        "",
        "## 📊 Distribution by Severity",
        "",
        "| Severity | Count | Percentage | Priority |",
        "|----------|-------|------------|----------|",
    ]

    severity_order = ['critical', 'high', 'medium', 'low', 'warning', 'note']
    for sev in severity_order:
        count = by_severity.get(sev, 0)
        if count > 0:
            pct = (count / total) * 100
            priority = 'P0' if sev == 'critical' else 'P1' if sev == 'high' else 'P2' if sev == 'medium' else 'P4'
            lines.append(f"| {sev.title()} | {count} | {pct:.1f}% | {priority} |")

    lines.extend([
        "",
        "## 🎯 Priority Breakdown",
        "",
        "| Priority | Count | SLA | Notes |",
        "|----------|-------|-----|-------|",
        f"| P0 | {len(priorities['P0'])} | 24 hours | Critical - High exploitability |",
        f"| P1 | {len(priorities['P1'])} | 3 days | High severity |",
        f"| P2 | {len(priorities['P2'])} | 1 week | Medium severity |",
        f"| P3 | {len(priorities['P3'])} | 2 weeks | Low severity |",
        f"| P4 | {len(priorities['P4'])} | 1 month | Informational |",
        "",
        "## 🔍 Vulnerability Categories",
        "",
        "| Category | Count | Percentage |",
        "|----------|-------|------------|",
    ])

    for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
        pct = (count / total) * 100
        lines.append(f"| {category} | {count} | {pct:.1f}% |")

    lines.extend([
        "",
        "## 📁 Top 20 Vulnerable Files",
        "",
        "| Rank | File | Alerts |",
        "|------|------|--------|",
    ])

    for rank, (file_path, count) in enumerate(by_file, 1):
        # Truncate long paths
        display_path = file_path if len(file_path) < 60 else "..." + file_path[-57:]
        lines.append(f"| {rank} | `{display_path}` | {count} |")

    lines.extend([
        "",
        "## 🛡️ CWE Distribution",
        "",
        "| CWE ID | Count | Percentage |",
        "|--------|-------|------------|",
    ])

    for cwe, count in sorted(by_cwe.items(), key=lambda x: -x[1])[:15]:
        pct = (count / total) * 100
        lines.append(f"| {cwe} | {count} | {pct:.1f}% |")

    lines.extend([
        "",
        "## 🚀 Recommended Actions",
        "",
        "### Immediate (P0 - 24 hours)",
        f"- Address {len(priorities['P0'])} critical alerts",
        "- Focus on injection vulnerabilities and authentication issues",
        "- Apply automated security codemods where possible",
        "",
        "### Short-term (P1 - 3 days)",
        f"- Resolve {len(priorities['P1'])} high severity alerts",
        "- Generate PRs for high-confidence fixes",
        "- Request security team review",
        "",
        "### Medium-term (P2/P3 - 1-2 weeks)",
        f"- Address {len(priorities['P2']) + len(priorities['P3'])} medium/low alerts",
        "- Batch process by vulnerability category",
        "- Document false positives",
        "",
        "## 📈 Automation Potential",
        "",
    ])

    # Estimate automation potential
    injection_count = sum(
        count for cat, count in by_category.items()
        if 'injection' in cat.lower()
    )
    traversal_count = by_category.get('path-traversal', 0)
    crypto_count = by_category.get('cryptography', 0)

    automatable = injection_count + traversal_count + crypto_count
    automation_pct = (automatable / total) * 100 if total > 0 else 0

    lines.extend([
        f"**Estimated Automation Coverage:** {automation_pct:.1f}% ({automatable}/{total} alerts)",
        "",
        "- Injection vulnerabilities: Can use parameterized query codemods",
        "- Path traversal: Can apply path sanitization utilities",
        "- Cryptography: Can update to secure algorithms",
        "",
        "## 🔗 Next Steps",
        "",
        "1. Extract P0/P1 alerts: `jq '.alerts[] | select(.severity == \"critical\" or .severity == \"high\")' alert_inventory.json`",
        "2. Apply security codemods: `python scripts/security/codemods/fix_*.py`",
        "3. Generate fix PRs: Use CodeQL Alert Resolution Agent",
        "4. Validate fixes: `python scripts/security/validate_security.py`",
        "5. Close alerts: `python scripts/security/close_codeql_alert.py`",
        "",
        "---",
        "",
        "**Report Generated By:** Phase 34 Alert Analysis Script",
        "**See Also:** `.codex/plans/CODEQL_ALERT_RESOLUTION_PLANSET.md`",
    ])

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✅ Analysis report written to: {output_path}")

    # Print summary to console
    print("\n" + "="*70)
    print("CODEQL ALERT ANALYSIS SUMMARY")
    print("="*70)
    print(f"Total Alerts: {total}")
    print("\nBy Priority:")
    for p in ['P0', 'P1', 'P2', 'P3', 'P4']:
        print(f"  {p}: {len(priorities[p])} alerts")
    print(f"\nAutomation Potential: {automation_pct:.1f}%")
    print(f"Top Category: {max(by_category.items(), key=lambda x: x[1])[0]} ({max(by_category.values())} alerts)")
    print("="*70)

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze CodeQL alert distribution and prioritization"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('.codex/security/alert_inventory.json'),
        help='Path to alert inventory JSON file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('.codex/security/alert_analysis.md'),
        help='Path to output analysis report'
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Alert inventory not found: {args.input}")
        print("Please fetch alerts first using: python scripts/security/fetch_codeql_alerts.py")
        return 1

    try:
        inventory = load_alert_inventory(args.input)
        generate_report(inventory, args.output)
        return 0
    except Exception as e:
        print(f"Error analyzing alerts: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
