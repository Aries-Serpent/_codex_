#!/usr/bin/env python3
"""
Quarterly Improvement Tracker

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/quarterly_improvement_tracker.py [options]

    Examples:
    $ python scripts/cognitive/quarterly_improvement_tracker.py --help

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



import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QuarterlyMetrics:
    """Metrics for a single quarter"""
    quarter: str  # e.g., "2024-Q1"
    start_date: str
    end_date: str
    metrics: dict[str, float]
    improvement_vs_previous: dict[str, float]
    targets_met: dict[str, bool]
    overall_score: float


class QuarterlyImprovementTracker:
    """Track and analyze quarterly improvements across all cognitive brain metrics"""

    def __init__(
        self,
        data_path: str = "cognitive/data",
        reports_path: str = "cognitive/reports",
        target_improvement: float = 0.05  # 5% quarterly improvement target
    ):
        self.data_path = Path(data_path)
        self.reports_path = Path(reports_path)
        self.target_improvement = target_improvement

        # Ensure directories exist
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)

        self.history: list[QuarterlyMetrics] = []
        self._load_history()

    def _load_history(self):
        """Load historical quarterly metrics"""
        history_file = self.reports_path / "quarterly_history.json"
        if history_file.exists():
            with open(history_file) as f:
                data = json.load(f)
                self.history = [
                    QuarterlyMetrics(**item) for item in data
                ]

    def _save_history(self):
        """Save quarterly metrics history"""
        history_file = self.reports_path / "quarterly_history.json"
        with open(history_file, 'w') as f:
            json.dump(
                [asdict(q) for q in self.history],
                f,
                indent=2
            )

    def get_quarter_dates(self, quarter: str) -> tuple[datetime, datetime]:
        """
        Get start and end dates for a quarter

        Args:
            quarter: Quarter string like "2024-Q1"

        Returns:
            Tuple of (start_date, end_date)
        """
        year, q = quarter.split('-')
        year = int(year)
        quarter_num = int(q[1])

        start_month = (quarter_num - 1) * 3 + 1
        start_date = datetime(year, start_month, 1)

        # End date is last day of last month in quarter
        if quarter_num < 4:
            end_date = datetime(year, start_month + 3, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, 12, 31)

        return start_date, end_date

    def collect_quarter_metrics(
        self,
        quarter: str,
        force_recalculate: bool = False
    ) -> QuarterlyMetrics:
        """
        Collect and aggregate all metrics for a quarter

        Args:
            quarter: Quarter string like "2024-Q1"
            force_recalculate: Force recalculation even if cached

        Returns:
            QuarterlyMetrics object with aggregated data
        """
        logger.info(f"Collecting metrics for {quarter}")

        # Check if already calculated
        if not force_recalculate:
            for qm in self.history:
                if qm.quarter == quarter:
                    logger.info(f"Using cached metrics for {quarter}")
                    return qm

        start_date, end_date = self.get_quarter_dates(quarter)

        # Collect metrics from various sources
        metrics = {
            # Perception Layer
            "pattern_detection_accuracy": self._get_metric_avg(
                "pattern_detection",
                "accuracy",
                start_date,
                end_date
            ),
            "anomaly_detection_precision": self._get_metric_avg(
                "anomaly_detection",
                "precision",
                start_date,
                end_date
            ),

            # Decision Engine
            "decision_latency_ms": self._get_metric_avg(
                "decision_engine",
                "latency_ms",
                start_date,
                end_date
            ),
            "causal_inference_accuracy": self._get_metric_avg(
                "causal_reasoning",
                "accuracy",
                start_date,
                end_date
            ),
            "optimization_efficiency": self._get_metric_avg(
                "resource_optimizer",
                "efficiency",
                start_date,
                end_date
            ),

            # Action Executor
            "task_success_rate": self._get_metric_avg(
                "action_executor",
                "success_rate",
                start_date,
                end_date
            ),
            "agent_utilization": self._get_metric_avg(
                "agent_dispatcher",
                "utilization",
                start_date,
                end_date
            ),

            # AfterMath Evaluator
            "learning_extraction_rate": self._get_metric_avg(
                "learning_extractor",
                "extraction_rate",
                start_date,
                end_date
            ),

            # Meta-Learning
            "pattern_reuse_rate": self._get_metric_avg(
                "meta_learning",
                "pattern_reuse",
                start_date,
                end_date
            ),
            "knowledge_transfer_efficiency": self._get_metric_avg(
                "meta_learning",
                "transfer_efficiency",
                start_date,
                end_date
            ),

            # Advanced Reasoning
            "explanation_quality": self._get_metric_avg(
                "shap_explainer",
                "quality_score",
                start_date,
                end_date
            ),
            "trust_score": self._get_metric_avg(
                "trust_dashboard",
                "overall_score",
                start_date,
                end_date
            ),

            # Full Autonomy
            "auto_fix_success_rate": self._get_metric_avg(
                "self_healing",
                "fix_success_rate",
                start_date,
                end_date
            ),
            "autonomous_decision_rate": self._get_metric_avg(
                "autonomous_decisions",
                "no_escalation_rate",
                start_date,
                end_date
            ),
            "coalition_performance_improvement": self._get_metric_avg(
                "agent_coalitions",
                "improvement_vs_individual",
                start_date,
                end_date
            ),
        }

        # Calculate improvements vs previous quarter
        improvements = {}
        targets_met = {}

        if self.history:
            previous = self.history[-1]
            for key, value in metrics.items():
                if key in previous.metrics and previous.metrics[key] > 0:
                    improvement = (value - previous.metrics[key]) / previous.metrics[key]
                    improvements[key] = improvement

                    # Check if target met (5-10% improvement)
                    targets_met[key] = (
                        self.target_improvement <= improvement <= 0.10
                    )
                else:
                    improvements[key] = 0.0
                    targets_met[key] = False
        else:
            # First quarter - no comparison
            improvements = {k: 0.0 for k in metrics}
            targets_met = {k: True for k in metrics}  # Consider all met for baseline

        # Calculate overall score
        overall_score = np.mean(list(metrics.values()))

        quarterly_metrics = QuarterlyMetrics(
            quarter=quarter,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            metrics=metrics,
            improvement_vs_previous=improvements,
            targets_met=targets_met,
            overall_score=overall_score
        )

        # Add to history and save
        self.history.append(quarterly_metrics)
        self._save_history()

        logger.info(f"Metrics collection complete for {quarter}")

        return quarterly_metrics

    def _get_metric_avg(
        self,
        component: str,
        metric_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Get average value of a specific metric for a date range

        Args:
            component: Component name (e.g., "pattern_detection")
            metric_name: Metric name (e.g., "accuracy")
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Average metric value
        """
        # Search for metric files
        metric_files = list(self.data_path.glob(f"{component}_*.json"))

        values = []
        for file in metric_files:
            try:
                with open(file) as f:
                    data = json.load(f)

                    # Handle different data formats
                    if isinstance(data, list):
                        for item in data:
                            if metric_name in item:
                                values.append(float(item[metric_name]))
                    elif isinstance(data, dict) and metric_name in data:
                        values.append(float(data[metric_name]))
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Could not parse metric from {file.name}: {e}")
                continue

        if values:
            return np.mean(values)

        # Return simulated baseline if no data
        return self._get_baseline_metric(component, metric_name)

    def _get_baseline_metric(self, component: str, metric_name: str) -> float:
        """Get baseline value for a metric (used when no data available)"""
        # Baseline values for different metric types
        baselines = {
            "accuracy": 0.75,
            "precision": 0.78,
            "recall": 0.76,
            "latency_ms": 3000.0,
            "efficiency": 0.85,
            "success_rate": 0.80,
            "utilization": 0.75,
            "extraction_rate": 0.70,
            "pattern_reuse": 0.55,
            "transfer_efficiency": 0.60,
            "quality_score": 0.88,
            "overall_score": 0.92,
            "fix_success_rate": 0.78,
            "no_escalation_rate": 0.85,
            "improvement_vs_individual": 0.45
        }

        return baselines.get(metric_name, 0.70)

    def analyze_trends(self, lookback_quarters: int = 4) -> dict[str, Any]:
        """
        Analyze trends across recent quarters

        Args:
            lookback_quarters: Number of quarters to analyze

        Returns:
            Dictionary with trend analysis
        """
        if len(self.history) < 2:
            return {
                "status": "insufficient_data",
                "message": "Need at least 2 quarters of data for trend analysis"
            }

        recent = self.history[-lookback_quarters:]

        # Calculate trend for each metric
        metric_trends = defaultdict(list)
        for qm in recent:
            for key, value in qm.metrics.items():
                metric_trends[key].append(value)

        # Analyze each metric trend
        trend_analysis = {}
        for metric, values in metric_trends.items():
            if len(values) >= 2:
                # Linear regression slope
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]

                # Percent change from first to last
                pct_change = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0.0

                trend_analysis[metric] = {
                    "slope": slope,
                    "percent_change": pct_change,
                    "direction": "improving" if slope > 0 else "declining",
                    "values": values
                }

        # Calculate overall improvement rate
        overall_improvements = [
            qm.improvement_vs_previous
            for qm in recent
            if qm.improvement_vs_previous
        ]

        if overall_improvements:
            avg_improvements_by_metric = {}
            for metric in trend_analysis:
                improvements = [
                    imp.get(metric, 0.0)
                    for imp in overall_improvements
                ]
                avg_improvements_by_metric[metric] = np.mean(improvements)

            overall_avg_improvement = np.mean(list(avg_improvements_by_metric.values()))
        else:
            overall_avg_improvement = 0.0
            avg_improvements_by_metric = {}

        # Count metrics meeting target
        targets_met_counts = [
            sum(qm.targets_met.values())
            for qm in recent
        ]

        return {
            "quarters_analyzed": len(recent),
            "metric_trends": trend_analysis,
            "overall_avg_improvement": overall_avg_improvement,
            "avg_improvements_by_metric": avg_improvements_by_metric,
            "targets_met_count": targets_met_counts,
            "target_achievement_rate": np.mean(targets_met_counts) / len(trend_analysis) if trend_analysis else 0.0
        }

    def generate_quarterly_report(
        self,
        quarter: str,
        include_visualizations: bool = False
    ) -> dict[str, Any]:
        """
        Generate comprehensive quarterly report

        Args:
            quarter: Quarter string like "2024-Q1"
            include_visualizations: Whether to generate visualization data

        Returns:
            Comprehensive report dictionary
        """
        # Collect metrics for this quarter
        quarterly_metrics = self.collect_quarter_metrics(quarter)

        # Analyze trends
        trends = self.analyze_trends()

        # Calculate summary statistics
        targets_met_count = sum(quarterly_metrics.targets_met.values())
        total_metrics = len(quarterly_metrics.metrics)
        target_achievement_rate = targets_met_count / total_metrics if total_metrics > 0 else 0.0

        # Identify top improvements and declines
        sorted_improvements = sorted(
            quarterly_metrics.improvement_vs_previous.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_improvements = sorted_improvements[:5]
        top_declines = sorted_improvements[-5:]

        report = {
            "quarter": quarter,
            "period": {
                "start": quarterly_metrics.start_date,
                "end": quarterly_metrics.end_date
            },
            "summary": {
                "overall_score": quarterly_metrics.overall_score,
                "targets_met_count": targets_met_count,
                "total_metrics": total_metrics,
                "target_achievement_rate": target_achievement_rate
            },
            "metrics": quarterly_metrics.metrics,
            "improvements": quarterly_metrics.improvement_vs_previous,
            "targets_met": quarterly_metrics.targets_met,
            "top_improvements": dict(top_improvements),
            "top_declines": dict(top_declines),
            "trend_analysis": trends
        }

        if include_visualizations:
            report["visualization_data"] = self._generate_visualization_data()

        # Save report
        report_file = self.reports_path / f"quarterly_report_{quarter}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate markdown report
        self._generate_markdown_report(report, quarter)

        logger.info(f"Quarterly report generated: {report_file}")

        return report

    def _generate_visualization_data(self) -> dict[str, Any]:
        """Generate data for visualizations"""
        if len(self.history) < 2:
            return {}

        # Time series data for key metrics
        quarters = [qm.quarter for qm in self.history]

        visualization_data = {
            "quarters": quarters,
            "time_series": {}
        }

        # Extract time series for each metric
        key_metrics = [
            "pattern_detection_accuracy",
            "decision_latency_ms",
            "task_success_rate",
            "trust_score",
            "auto_fix_success_rate"
        ]

        for metric in key_metrics:
            visualization_data["time_series"][metric] = [
                qm.metrics.get(metric, 0.0)
                for qm in self.history
            ]

        return visualization_data

    def _generate_markdown_report(self, report: dict[str, Any], quarter: str):
        """Generate markdown version of quarterly report"""
        md_content = f"""# Quarterly Improvement Report: {quarter}

## Executive Summary

**Period**: {report['period']['start']} to {report['period']['end']}
**Overall Score**: {report['summary']['overall_score']:.2%}
**Targets Met**: {report['summary']['targets_met_count']}/{report['summary']['total_metrics']} ({report['summary']['target_achievement_rate']:.1%})

---

## Top Improvements

"""

        for metric, improvement in report['top_improvements'].items():
            emoji = "✅" if improvement >= self.target_improvement else "⚠️"
            md_content += f"- {emoji} **{metric}**: {improvement:+.2%}\n"

        md_content += "\n## Areas Needing Attention\n\n"

        for metric, improvement in report['top_declines'].items():
            emoji = "❌" if improvement < 0 else "⚠️"
            md_content += f"- {emoji} **{metric}**: {improvement:+.2%}\n"

        md_content += "\n## Trend Analysis\n\n"

        if report['trend_analysis'].get('overall_avg_improvement'):
            md_content += f"**Overall Average Improvement**: {report['trend_analysis']['overall_avg_improvement']:+.2%}\n\n"

        # Save markdown
        md_file = self.reports_path / f"quarterly_report_{quarter}.md"
        with open(md_file, 'w') as f:
            f.write(md_content)


def main():
    """Main entry point for quarterly tracking"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Quarterly improvement tracker"
    )
    parser.add_argument(
        "--quarter",
        help="Quarter to analyze (e.g., '2024-Q1'). If not specified, uses current quarter."
    )
    parser.add_argument(
        "--analyze-trends",
        action="store_true",
        help="Analyze trends across recent quarters"
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=4,
        help="Number of quarters to analyze for trends"
    )

    args = parser.parse_args()

    # Initialize tracker
    tracker = QuarterlyImprovementTracker()

    # Determine quarter
    if args.quarter:
        quarter = args.quarter
    else:
        # Calculate current quarter
        now = datetime.now()
        quarter_num = (now.month - 1) // 3 + 1
        quarter = f"{now.year}-Q{quarter_num}"

    # Generate report
    report = tracker.generate_quarterly_report(
        quarter=quarter,
        include_visualizations=True
    )

    print(f"\n{'='*60}")
    print(f"QUARTERLY REPORT: {quarter}")
    print(f"{'='*60}\n")
    print(json.dumps(report, indent=2))

    # Analyze trends if requested
    if args.analyze_trends:
        trends = tracker.analyze_trends(lookback_quarters=args.lookback)
        print(f"\n{'='*60}")
        print("TREND ANALYSIS")
        print(f"{'='*60}\n")
        print(json.dumps(trends, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
