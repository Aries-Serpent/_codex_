#!/usr/bin/env python3
"""
Workflow Health Dashboard Generator - Phase 5 Continuous Monitoring

Generates a comprehensive health dashboard from collected metrics.
Creates a markdown file suitable for GitHub display.

Usage:
    python scripts/ci/workflow_health_dashboard.py --input .codex/workflow_health_snapshot.json --output .codex/WORKFLOW_HEALTH_DASHBOARD.md
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Generates health dashboard from metrics"""

    def __init__(self, metrics_file: str):
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
        self.critical_workflows = ["codeql.yml", "test-comprehensive.yml", "security.yml"]

    def _load_metrics(self) -> Dict:
        """Load metrics from JSON file"""
        try:
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Metrics file not found: {self.metrics_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in metrics file: {e}")
            return {}

    def _get_status_emoji(self, success_rate: float) -> str:
        """Get emoji for status"""
        if success_rate >= 95:
            return "🟢"
        elif success_rate >= 80:
            return "🟡"
        else:
            return "🔴"

    def _get_trend_arrow(self, trend: str) -> str:
        """Get arrow for trend"""
        if trend == "improving":
            return "📈"
        elif trend == "degrading":
            return "📉"
        else:
            return "➡️"

    def _format_seconds(self, seconds: int) -> str:
        """Format seconds to readable time"""
        if seconds < 60:
            return f"{seconds}s"
        minutes = seconds // 60
        secs = seconds % 60
        if secs == 0:
            return f"{minutes}m"
        return f"{minutes}m {secs}s"

    def _sort_workflows(self, metrics: Dict) -> List[Tuple[str, Dict]]:
        """Sort workflows by criticality and status"""
        items = []
        
        for name, data in metrics.get("metrics", {}).items():
            success_rate = data.get("success_rate", 0)
            items.append((name, data, success_rate))

        # Sort: critical first, then by success rate (lowest first)
        def sort_key(item):
            name, data, success_rate = item
            is_critical = any(crit in name for crit in self.critical_workflows)
            return (not is_critical, success_rate)

        sorted_items = sorted(items, key=sort_key)
        return [(name, data) for name, data, _ in sorted_items]

    def _generate_critical_section(self, sorted_workflows: List[Tuple[str, Dict]]) -> str:
        """Generate critical issues section"""
        critical = [(name, data) for name, data in sorted_workflows 
                   if data.get("success_rate", 100) < 80]

        if not critical:
            return ""

        lines = ["## 🔴 Critical Issues (Action Required)\n"]
        lines.append("| Workflow | Status | Success Rate | Last Run | Issue |")
        lines.append("|----------|--------|--------------|----------|-------|")

        for name, data in critical:
            status_emoji = self._get_status_emoji(data.get("success_rate", 0))
            success_rate = data.get("success_rate", 0)
            last_status = data.get("last_run_status", "unknown")
            failed = data.get("failed_runs", 0)
            total = data.get("total_runs", 0)

            issue = f"{failed}/{total} failed" if total > 0 else "No data"
            
            lines.append(f"| {name} | {status_emoji} | {success_rate}% | {last_status} | {issue} |")

        return "\n".join(lines) + "\n"

    def _generate_warning_section(self, sorted_workflows: List[Tuple[str, Dict]]) -> str:
        """Generate warning section"""
        warnings = [(name, data) for name, data in sorted_workflows 
                   if 80 <= data.get("success_rate", 100) < 95]

        if not warnings:
            return ""

        lines = ["## 🟡 Warnings (Monitor Closely)\n"]
        lines.append("| Workflow | Success Rate | Avg Runtime | P95 Runtime | Trend | Status |")
        lines.append("|----------|--------------|-------------|-------------|-------|--------|")

        for name, data in warnings:
            status_emoji = self._get_status_emoji(data.get("success_rate", 0))
            success_rate = data.get("success_rate", 0)
            avg_runtime = self._format_seconds(data.get("average_runtime_seconds", 0))
            p95_runtime = self._format_seconds(data.get("p95_runtime_seconds", 0))
            trend = self._get_trend_arrow(data.get("trend", "stable"))

            lines.append(f"| {name} | {success_rate}% | {avg_runtime} | {p95_runtime} | {trend} | {status_emoji} |")

        return "\n".join(lines) + "\n"

    def _generate_healthy_section(self, sorted_workflows: List[Tuple[str, Dict]]) -> str:
        """Generate healthy workflows section"""
        healthy = [(name, data) for name, data in sorted_workflows 
                  if data.get("success_rate", 0) >= 95]

        if not healthy:
            return ""

        lines = ["## 🟢 Healthy Workflows\n"]
        lines.append("| Workflow | Success Rate | Avg Runtime | P95 Runtime | Runs | Last Run |")
        lines.append("|----------|--------------|-------------|-------------|------|----------|")

        for name, data in healthy[:20]:  # Limit to 20 for readability
            success_rate = data.get("success_rate", 0)
            avg_runtime = self._format_seconds(data.get("average_runtime_seconds", 0))
            p95_runtime = self._format_seconds(data.get("p95_runtime_seconds", 0))
            total_runs = data.get("total_runs", 0)
            last_status = data.get("last_run_status", "unknown")

            lines.append(f"| {name} | {success_rate}% | {avg_runtime} | {p95_runtime} | {total_runs} | {last_status} |")

        if len(healthy) > 20:
            lines.append(f"\n*(+{len(healthy) - 20} more healthy workflows)*\n")

        return "\n".join(lines) + "\n"

    def _generate_metrics_section(self, summary: Dict) -> str:
        """Generate performance metrics section"""
        lines = ["## 📈 Performance Metrics\n"]
        
        avg_success = summary.get("avg_success_rate", 0)
        min_success = summary.get("min_success_rate", 0)
        total_workflows = summary.get("total_workflows", 0)
        workflows_95 = summary.get("workflows_above_95_percent", 0)
        workflows_80 = summary.get("workflows_below_80_percent", 0)
        
        lines.append(f"- **Total Workflows**: {total_workflows}")
        lines.append(f"- **Average Success Rate**: {avg_success}% (target: >95%)")
        lines.append(f"- **Lowest Success Rate**: {min_success}%")
        lines.append(f"- **Workflows Meeting Target (≥95%)**: {workflows_95}/{total_workflows}")
        lines.append(f"- **Workflows Below 80%**: {workflows_80} ⚠️")
        
        return "\n".join(lines) + "\n"

    def _generate_codeql_section(self, sorted_workflows: List[Tuple[str, Dict]]) -> str:
        """Generate CodeQL specific section"""
        lines = ["## 🔒 CodeQL Specific KPIs\n"]
        
        # Find CodeQL workflows
        codeql_workflows = [(name, data) for name, data in sorted_workflows 
                          if "codeql" in name.lower()]

        if not codeql_workflows:
            lines.append("*No CodeQL-specific workflows found*\n")
            return "\n".join(lines) + "\n"

        for name, data in codeql_workflows:
            success_rate = data.get("success_rate", 0)
            status_emoji = self._get_status_emoji(success_rate)
            total_runs = data.get("total_runs", 0)
            successful = data.get("successful_runs", 0)

            lines.append(f"- **{name}**: {status_emoji} {success_rate}% ({successful}/{total_runs})")

        lines.append("\n**Target**: CodeQL success rate ≥99%\n")
        
        return "\n".join(lines) + "\n"

    def _generate_actions_section(self) -> str:
        """Generate recommended actions section"""
        lines = ["## 🎯 Recommended Actions\n"]
        
        sorted_workflows = self._sort_workflows(self.metrics)
        critical = [(name, data) for name, data in sorted_workflows 
                   if data.get("success_rate", 100) < 80]

        if critical:
            lines.append("### Immediate Actions (Critical)\n")
            for name, data in critical[:5]:
                lines.append(f"- [ ] Investigate `{name}` ({data.get('success_rate')}% success)")
                lines.append(f"      - Last {data.get('total_runs')} runs: "
                            f"{data.get('failed_runs')} failures, "
                            f"{data.get('cancelled_runs')} cancellations")
        
        return "\n".join(lines) + "\n"

    def _generate_footer(self) -> str:
        """Generate footer section"""
        generated_at = self.metrics.get("generated_at", datetime.utcnow().isoformat())
        
        return f"""
---

**Dashboard Generated**: {generated_at}
**Next Update**: {(datetime.fromisoformat(generated_at.replace('Z', '+00:00')) + __import__('datetime').timedelta(days=1)).isoformat()}

[View Health Data](.codex/workflow_health_snapshot.json) | [Optimization Decisions](.codex/WORKFLOW_OPTIMIZATION_DECISIONS.md)

*Generated by Phase 5 Continuous Enablement Monitoring | Automation: `.github/workflows/workflow-health-update.yml`*
"""

    def generate(self) -> str:
        """Generate complete dashboard"""
        if not self.metrics:
            logger.error("No metrics loaded")
            return ""

        lines = ["# Workflow Health Dashboard\n"]
        
        generated_at = self.metrics.get("generated_at", datetime.utcnow().isoformat())
        lines.append(f"**Generated**: {generated_at}\n")
        lines.append(f"**Coverage**: Last 30 days\n")
        lines.append(f"**Refresh**: Daily at 02:00 UTC\n\n")

        sorted_workflows = self._sort_workflows(self.metrics)
        summary = self.metrics.get("summary", {})

        # Add sections
        lines.append(self._generate_critical_section(sorted_workflows))
        lines.append(self._generate_warning_section(sorted_workflows))
        lines.append(self._generate_metrics_section(summary))
        lines.append(self._generate_codeql_section(sorted_workflows))
        lines.append(self._generate_healthy_section(sorted_workflows))
        lines.append(self._generate_actions_section())
        lines.append(self._generate_footer())

        return "".join(lines)

    def save(self, output_file: str):
        """Save dashboard to file"""
        dashboard_content = self.generate()
        
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(dashboard_content)
        
        logger.info(f"Dashboard saved to {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate workflow health dashboard")
    parser.add_argument("--input", type=str, required=True, help="Input metrics JSON file")
    parser.add_argument("--output", type=str, default=".codex/WORKFLOW_HEALTH_DASHBOARD.md", help="Output markdown file")
    
    args = parser.parse_args()

    try:
        generator = DashboardGenerator(args.input)
        generator.save(args.output)
        logger.info("✅ Dashboard generation complete")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
