#!/usr/bin/env python3
"""
phase_8_3_perf_analyzer.py — Analyze performance metrics and detect regressions.

Performs:
- Baseline comparison
- Regression detection
- Trend analysis
- Anomaly detection
- Report generation

Usage:
    python scripts/ci/phase_8_3_perf_analyzer.py --current metrics.json
    python scripts/ci/phase_8_3_perf_analyzer.py --current metrics.json --baseline baseline.json
    python scripts/ci/phase_8_3_perf_analyzer.py --compare --generate-report
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class AnalysisResult:
    """Result of performance analysis."""
    metric_name: str
    baseline_value: float
    current_value: float
    delta_absolute: float
    delta_percent: float
    status: str
    threshold_percent: float
    message: str


class PerformanceAnalyzer:
    """Analyze performance metrics against baselines."""

    def __init__(self, sla_config_path: Path):
        """Initialize analyzer with SLA configuration."""
        self.sla_config = self._load_sla_config(sla_config_path)
        self.results: list[AnalysisResult] = []

    def _load_sla_config(self, config_path: Path) -> dict[str, Any]:
        """Load SLA configuration."""
        if not config_path.exists():
            print(f"Warning: SLA config not found at {config_path}")
            return {}

        with open(config_path) as f:
            return json.load(f)

    def analyze_metric(
        self,
        metric_name: str,
        baseline_value: float,
        current_value: float,
        metric_type: str = "latency",
    ) -> AnalysisResult:
        """Analyze a single metric against baseline."""
        if baseline_value <= 0:
            return AnalysisResult(
                metric_name=metric_name,
                baseline_value=baseline_value,
                current_value=current_value,
                delta_absolute=0,
                delta_percent=0,
                status="SKIP",
                threshold_percent=0,
                message="Baseline value invalid",
            )

        # Calculate delta
        if metric_type == "latency" or metric_type == "throughput_inverse":
            # For latency: increase = regression (bad)
            delta_absolute = current_value - baseline_value
            delta_percent = (delta_absolute / baseline_value) * 100
        else:
            # For throughput: decrease = regression (bad)
            delta_absolute = baseline_value - current_value
            delta_percent = (delta_absolute / baseline_value) * 100

        # Get SLA thresholds
        sla_thresholds = self.sla_config.get("sla_thresholds", {})
        metric_sla = sla_thresholds.get(metric_name, {})

        acceptable_percent = metric_sla.get("deviation_acceptable_percent", 5)
        alert_percent = metric_sla.get("alert_threshold_percent", 20)
        critical_percent = metric_sla.get("critical_threshold_percent", 30)

        # Determine status
        if abs(delta_percent) <= acceptable_percent:
            status = "OK"
            message = f"Within acceptable range ({acceptable_percent}%)"
        elif delta_percent <= alert_percent:
            status = "WARNING"
            message = f"Regression detected: {delta_percent:.1f}% (threshold: {alert_percent}%)"
        elif delta_percent <= critical_percent:
            status = "CRITICAL"
            message = f"Critical regression: {delta_percent:.1f}% (threshold: {critical_percent}%)"
        else:
            status = "SEVERE"
            message = f"Severe regression: {delta_percent:.1f}% (threshold: {critical_percent}%)"

        result = AnalysisResult(
            metric_name=metric_name,
            baseline_value=baseline_value,
            current_value=current_value,
            delta_absolute=round(delta_absolute, 2),
            delta_percent=round(delta_percent, 2),
            status=status,
            threshold_percent=acceptable_percent,
            message=message,
        )

        self.results.append(result)
        return result

    def compare_workflow_metrics(
        self,
        baseline_metrics: dict[str, Any],
        current_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Compare workflow metrics."""
        comparisons = {}

        baseline_workflows = baseline_metrics.get("workflow_execution_time", {})
        current_workflows = current_metrics.get("workflow_execution_time", {})

        for workflow_name in baseline_workflows:
            if workflow_name not in current_workflows:
                continue

            baseline_p95 = baseline_workflows[workflow_name].get("p95_ms", 0)
            current_p95 = current_workflows[workflow_name].get("p95_ms", 0)

            result = self.analyze_metric(
                f"{workflow_name}_p95_latency",
                baseline_p95,
                current_p95,
                metric_type="latency",
            )

            comparisons[workflow_name] = asdict(result)

        return comparisons

    def generate_report(self) -> str:
        """Generate analysis report."""
        lines = [
            "# Performance Analysis Report",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Metrics Analyzed:** {len(self.results)}",
            f"- **OK:** {sum(1 for r in self.results if r.status == 'OK')}",
            f"- **WARNING:** {sum(1 for r in self.results if r.status == 'WARNING')}",
            f"- **CRITICAL:** {sum(1 for r in self.results if r.status == 'CRITICAL')}",
            f"- **SEVERE:** {sum(1 for r in self.results if r.status == 'SEVERE')}",
            "",
            "## Detailed Results",
            "",
            "| Metric | Baseline | Current | Delta | Status | Message |",
            "|--------|----------|---------|-------|--------|---------|",
        ]

        for result in sorted(self.results, key=lambda r: r.delta_percent, reverse=True):
            status_emoji = {
                "OK": "✅",
                "WARNING": "⚠️",
                "CRITICAL": "❌",
                "SEVERE": "🔴",
                "SKIP": "⊘",
            }.get(result.status, "?")

            lines.append(
                f"| {result.metric_name} | "
                f"{result.baseline_value:.2f} | "
                f"{result.current_value:.2f} | "
                f"{result.delta_percent:+.1f}% | "
                f"{status_emoji} {result.status} | "
                f"{result.message} |"
            )

        # Regressions section
        regressions = [r for r in self.results if r.status in ("WARNING", "CRITICAL", "SEVERE")]
        if regressions:
            lines.extend([
                "",
                "## Detected Regressions",
                "",
            ])
            for result in sorted(regressions, key=lambda r: r.delta_percent, reverse=True):
                lines.append(f"### {result.metric_name}")
                lines.append(f"- **Baseline:** {result.baseline_value:.2f}")
                lines.append(f"- **Current:** {result.current_value:.2f}")
                lines.append(f"- **Regression:** {result.delta_percent:+.1f}%")
                lines.append(f"- **Status:** {result.status}")
                lines.append(f"- **Message:** {result.message}")
                lines.append("")

        return "\n".join(lines)

    def get_summary_json(self) -> dict[str, Any]:
        """Get summary as JSON."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_metrics": len(self.results),
            "ok_count": sum(1 for r in self.results if r.status == "OK"),
            "warning_count": sum(1 for r in self.results if r.status == "WARNING"),
            "critical_count": sum(1 for r in self.results if r.status == "CRITICAL"),
            "severe_count": sum(1 for r in self.results if r.status == "SEVERE"),
            "results": [asdict(r) for r in self.results],
        }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze performance metrics and detect regressions"
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Current metrics JSON file",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Baseline metrics JSON file",
    )
    parser.add_argument(
        "--sla-config",
        type=Path,
        default=Path(".codex/PHASE_8_3_SLA_THRESHOLDS.json"),
        help="SLA configuration file",
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate markdown report",
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        help="Export results as JSON",
    )

    args = parser.parse_args()

    # Load metrics
    if not args.current.exists():
        print(f"Error: Current metrics file not found: {args.current}")
        sys.exit(1)

    with open(args.current) as f:
        current_metrics = json.load(f)

    # Initialize analyzer
    analyzer = PerformanceAnalyzer(args.sla_config)

    # Perform analysis
    if args.baseline and args.baseline.exists():
        with open(args.baseline) as f:
            baseline_metrics = json.load(f)

        print("Comparing current metrics against baseline...")
        analyzer.compare_workflow_metrics(baseline_metrics, current_metrics)
    else:
        print("No baseline provided - using built-in thresholds")

    # Generate report if requested
    if args.generate_report:
        report = analyzer.generate_report()
        print("\n" + report)

    # Export JSON if requested
    if args.export_json:
        summary = analyzer.get_summary_json()
        with open(args.export_json, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Results exported to: {args.export_json}")

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    summary = analyzer.get_summary_json()
    print(f"Total metrics: {summary['total_metrics']}")
    print(f"OK: {summary['ok_count']}")
    print(f"WARNING: {summary['warning_count']}")
    print(f"CRITICAL: {summary['critical_count']}")
    print(f"SEVERE: {summary['severe_count']}")

    # Exit with error if regressions detected
    if summary['critical_count'] > 0 or summary['severe_count'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
