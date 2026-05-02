#!/usr/bin/env python3
"""Monitor CI health and generate actionable reports."""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class CIHealthMonitor:
    """Monitor and report on CI health patterns."""

    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root)
        self.patterns = defaultdict(int)

    def analyze_workflow_logs(self, workflow_dir=".github/workflows"):
        """Analyze workflow configurations for common issues."""
        issues = []
        workflow_path = self.repo_root / workflow_dir

        for workflow_file in workflow_path.glob("*.yml"):
            content = workflow_file.read_text()

            # Check for missing timeout-minutes
            if "timeout-minutes" not in content:
                issues.append(f"⚠️ {workflow_file.name}: Missing timeout-minutes configuration")

            # Check for artifact upload without if: always()
            if "upload-artifact" in content and "if: always()" not in content:
                issues.append(f"⚠️ {workflow_file.name}: Artifact upload may be skipped on failure")

            # Check for tests without timeout
            if "pytest" in content and "--timeout" not in content:
                issues.append(f"⚠️ {workflow_file.name}: Tests may hang without timeout")

        return issues

    def generate_health_report(self):
        """Generate comprehensive health report."""
        issues = self.analyze_workflow_logs()

        return {
            "timestamp": datetime.now().isoformat(),
            "issues_found": len(issues),
            "issues": issues,
            "recommendations": self._generate_recommendations(issues)
        }


    def _generate_recommendations(self, issues):
        """Generate actionable recommendations."""
        recommendations = []

        if any("timeout-minutes" in issue for issue in issues):
            recommendations.append({
                "priority": "HIGH",
                "action": "Add timeout-minutes to all workflow jobs",
                "fix": "Add 'timeout-minutes: 60' to job definitions"
            })

        if any("upload-artifact" in issue for issue in issues):
            recommendations.append({
                "priority": "HIGH",
                "action": "Make artifact uploads resilient",
                "fix": "Add 'if: always()' to upload-artifact steps"
            })

        if any("pytest" in issue for issue in issues):
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Add test timeouts",
                "fix": "Use 'pytest --timeout=300' in workflows"
            })

        return recommendations

if __name__ == "__main__":
    monitor = CIHealthMonitor()
    report = monitor.generate_health_report()

    print("# CI Health Report")
    print(f"Generated: {report['timestamp']}")
    print(f"\n## Issues Found: {report['issues_found']}")

    for issue in report['issues']:
        print(f"  - {issue}")

    print("\n## Recommendations:")
    for rec in report['recommendations']:
        print(f"  [{rec['priority']}] {rec['action']}")
        print(f"      Fix: {rec['fix']}")

    # Exit with error if critical issues found
    sys.exit(1 if report['issues_found'] > 0 else 0)
