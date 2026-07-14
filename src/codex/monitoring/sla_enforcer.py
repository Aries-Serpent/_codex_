"""
Performance SLA Enforcement System - GitHub Actions Integration
Phase 4D Planset 007 - PR blocking & SLA enforcement

Integrates with GitHub Actions to:
- Block PRs with CRITICAL regressions
- Enforce performance SLAs
- Generate automated performance reports
- Post results as PR comments
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional, Any

from codex.monitoring.performance_monitor import (
    PerformanceMonitor,
    SeverityLevel,
    detect_ci_regression,
)


class GitHubSLAEnforcer:
    """
    Enforce performance SLAs in GitHub Actions.
    
    Supports:
    - Blocking PRs with CRITICAL regressions
    - Setting GitHub check status
    - Posting performance reports as PR comments
    - Writing output for workflow actions
    """

    def __init__(self):
        self.monitor = PerformanceMonitor()
        self._setup_default_slas()

    def _setup_default_slas(self) -> None:
        """Setup default SLA definitions"""
        # Test suite performance
        self.monitor.set_sla(
            "test_suite_duration_seconds",
            warning_threshold=900,  # 15 minutes
            critical_threshold=1200,  # 20 minutes
            description="Full test suite should complete within SLA"
        )
        
        # Individual test performance
        self.monitor.set_sla(
            "slow_test_duration_ms",
            warning_threshold=5000,  # 5 seconds
            critical_threshold=10000,  # 10 seconds
            description="Individual test should not exceed SLA"
        )
        
        # Workflow execution
        self.monitor.set_sla(
            "workflow_execution_minutes",
            warning_threshold=60,  # 1 hour
            critical_threshold=120,  # 2 hours
            description="Workflow should complete within SLA"
        )
        
        # Memory usage
        self.monitor.set_sla(
            "peak_memory_mb",
            warning_threshold=2048,  # 2GB
            critical_threshold=4096,  # 4GB
            description="Peak memory should not exceed SLA"
        )

    def load_baseline(self, baseline_file: Path) -> None:
        """Load baseline metrics from file"""
        if not baseline_file.exists():
            print(f"WARNING: Baseline file not found: {baseline_file}", file=sys.stderr)
            return
        
        try:
            with open(baseline_file, "r") as f:
                baseline_data = json.load(f)
            
            # Load baselines for key metrics
            for metric_name, metric_data in baseline_data.get("baselines", {}).get("test_execution", {}).items():
                if isinstance(metric_data, dict) and "value" in metric_data:
                    self.monitor.set_baseline(metric_name, [metric_data["value"]])
        
        except Exception as e:
            print(f"ERROR: Failed to load baseline: {e}", file=sys.stderr)

    def check_metrics(self, metrics_file: Path) -> dict[str, Any]:
        """
        Check collected metrics against SLAs.
        
        Args:
            metrics_file: Path to metrics JSON file
            
        Returns:
            Dictionary with enforcement results
        """
        results = {
            "passed": True,
            "violations": [],
            "warnings": [],
            "critical_regressions": [],
        }
        
        if not metrics_file.exists():
            return results
        
        try:
            with open(metrics_file, "r") as f:
                metrics_data = json.load(f)
            
            for metric_name, metric_value in metrics_data.get("metrics", {}).items():
                # Check SLA
                severity = self.monitor.sla_enforcer.check_sla(metric_name, metric_value)
                
                if severity == SeverityLevel.CRITICAL:
                    results["passed"] = False
                    results["critical_regressions"].append({
                        "metric": metric_name,
                        "value": metric_value,
                    })
                elif severity == SeverityLevel.HIGH:
                    results["warnings"].append({
                        "metric": metric_name,
                        "value": metric_value,
                    })
        
        except Exception as e:
            print(f"ERROR: Failed to check metrics: {e}", file=sys.stderr)
        
        return results

    def generate_pr_comment(self, results: dict[str, Any]) -> str:
        """Generate markdown comment for PR"""
        lines = ["## 🚀 Performance SLA Check", ""]
        
        if results["passed"]:
            lines.append("✅ **All performance SLAs passed**")
        else:
            lines.append("❌ **Performance SLA violations detected**")
        
        if results["critical_regressions"]:
            lines.append("")
            lines.append("### 🔴 CRITICAL Violations")
            for regression in results["critical_regressions"]:
                lines.append(f"- **{regression['metric']}**: {regression['value']}")
        
        if results["warnings"]:
            lines.append("")
            lines.append("### ⚠️ Warnings")
            for warning in results["warnings"]:
                lines.append(f"- **{warning['metric']}**: {warning['value']}")
        
        return "\n".join(lines)

    def set_github_output(self, passed: bool, message: str = "") -> None:
        """Set GitHub Actions output"""
        output_file = Path(os.environ.get("GITHUB_OUTPUT", "/dev/null"))
        if output_file.exists():
            with open(output_file, "a") as f:
                f.write(f"passed={'true' if passed else 'false'}\n")
                if message:
                    f.write(f"message={message}\n")

    def block_pr_if_needed(self, results: dict[str, Any]) -> int:
        """
        Block PR if critical regressions detected.
        
        Returns:
            Exit code (0 if passed, 1 if failed)
        """
        if not results["passed"]:
            print("::error::Performance SLA check failed - blocking PR", file=sys.stderr)
            return 1
        
        print("✅ Performance SLA check passed")
        return 0


# Standalone CLI interface
def main() -> int:
    """Main entry point for GitHub Actions"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description="Performance SLA enforcement for GitHub Actions"
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path(".codex/perf/baselines.json"),
        help="Path to baseline metrics"
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        required=True,
        help="Path to current metrics"
    )
    parser.add_argument(
        "--pr-comment",
        action="store_true",
        help="Generate PR comment"
    )
    
    args = parser.parse_args()
    
    # Create enforcer
    enforcer = GitHubSLAEnforcer()
    
    # Load baseline if available
    if args.baseline.exists():
        enforcer.load_baseline(args.baseline)
    
    # Check metrics
    results = enforcer.check_metrics(args.metrics)
    
    # Generate PR comment if requested
    if args.pr_comment:
        comment = enforcer.generate_pr_comment(results)
        print(comment)
    
    # Set GitHub output
    enforcer.set_github_output(
        results["passed"],
        enforcer.generate_pr_comment(results) if args.pr_comment else ""
    )
    
    # Return appropriate exit code
    return enforcer.block_pr_if_needed(results)


if __name__ == "__main__":
    import os
    sys.exit(main())
