#!/usr/bin/env python3
"""
Generate PR comment with quality metrics summary.

Creates a formatted markdown comment for GitHub PRs.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None


def generate_pr_comment(
    metrics_dir: str,
    slos_yaml: str,
    alert_policy_md: str,
    output_path: str
) -> None:
    """Generate PR comment with metrics summary."""
    
    # Load metrics
    metrics_path = Path(metrics_dir)
    
    coverage_data = {}
    module_coverage = {}
    slo_compliance = {}
    
    try:
        with open(metrics_path / "coverage_latest.json") as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        pass
    
    try:
        with open(metrics_path / "module_coverage_latest.json") as f:
            module_coverage = json.load(f)
    except FileNotFoundError:
        pass
    
    try:
        with open(metrics_path / "slo_compliance_latest.json") as f:
            slo_compliance = json.load(f)
    except FileNotFoundError:
        pass
    
    # Build comment
    comment = []
    comment.append("## 📊 Quality Metrics Report")
    comment.append("")
    
    # Coverage section
    coverage = coverage_data.get('value', 0)
    target = coverage_data.get('target', 70)
    status = coverage_data.get('status', 'unknown')
    
    if coverage >= target:
        emoji = "✅"
    elif coverage >= target * 0.8:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    comment.append(f"### Coverage {emoji}")
    comment.append(f"- **Overall**: {coverage:.2f}% (target: {target}%)")
    comment.append(f"- **Status**: {status.replace('_', ' ').title()}")
    comment.append("")
    
    # SLO compliance section
    if slo_compliance:
        compliance = slo_compliance.get('compliance', {})
        compliance_pct = slo_compliance.get('compliance_percentage', 0)
        
        if compliance_pct >= 80:
            emoji = "✅"
        elif compliance_pct >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        comment.append(f"### SLO Compliance {emoji}")
        comment.append(f"- **Compliance**: {compliance_pct:.1f}%")
        comment.append(f"- **Compliant**: {compliance.get('compliant_modules', 0)}/{compliance.get('total_modules', 0)} modules")
        
        non_compliant = compliance.get('non_compliant_modules', [])
        if non_compliant:
            comment.append("- **Non-Compliant Modules**:")
            for module in non_compliant[:5]:  # Top 5
                gap = module.get('gap', 0)
                comment.append(f"  - {module['module']}: {module['actual']:.1f}% (need {gap:.1f}% more)")
        comment.append("")
    
    # Recommendations
    comment.append("### 📝 Next Steps")
    
    if coverage < 50:
        comment.append("1. Focus on coverage for critical modules (auth, data validation, API)")
        comment.append("2. Review coverage report: check htmlcov/index.html")
        comment.append("3. Add tests for uncovered paths in your changes")
    elif coverage < target:
        comment.append("1. Review per-module coverage in SLO table")
        comment.append("2. Focus on modules below their SLO targets")
        comment.append("3. Add targeted tests for low-coverage areas")
    else:
        comment.append("✅ Coverage targets met! Continue maintaining high coverage.")
    
    comment.append("")
    comment.append("**Dashboard**: [Quality Dashboard](https://github.com/aries-serpent/_codex_/projects)")
    comment.append("**Documentation**: [Phase 5 Metrics Guide](../../docs/quality_dashboard/DASHBOARD_README.md)")
    
    # Write comment
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(comment))
    
    print(f"✅ PR comment generated at {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: generate_pr_comment.py <metrics_dir> <slos.yaml> <alert_policy.md> <output.md>")
        sys.exit(1)
    
    generate_pr_comment(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
