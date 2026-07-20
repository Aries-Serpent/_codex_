#!/usr/bin/env python3
"""
Telemetry and Monitoring for Self-Healing CI Infrastructure

Collects and tracks:
- Recovery success rates by pattern
- Mean Time To Recovery (MTTR)
- Failure trend analysis
- AAIS Reliability score metrics
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


@dataclass
class MetricsSnapshot:
    """Point-in-time metrics snapshot."""

    timestamp: str
    total_failures: int
    total_recoveries: int
    recovery_rate_pct: float
    mttr_seconds: float
    unique_patterns: int
    top_patterns: List[Dict]
    aais_reliability_delta: float


class TelemetryCollector:
    """Collect and aggregate telemetry from CI runs."""

    def __init__(self, data_dir: str = ".codex/telemetry"):
        """
        Initialize telemetry collector.

        Parameters
        ----------
        data_dir : str
            Directory for telemetry data storage
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_file = self.data_dir / "recovery-attempts.jsonl"
        self.metrics_file = self.data_dir / "metrics-snapshots.json"
        self.dashboard_file = self.data_dir / "dashboard.json"

    def record_recovery_attempt(self, attempt: Dict) -> None:
        """Record a single recovery attempt in JSONL format."""
        with open(self.recovery_file, "a") as f:
            f.write(json.dumps(attempt) + "\n")

    def read_recovery_attempts(self) -> List[Dict]:
        """Read all recorded recovery attempts."""
        if not self.recovery_file.exists():
            return []

        attempts = []
        with open(self.recovery_file, "r") as f:
            for line in f:
                if line.strip():
                    attempts.append(json.loads(line))
        return attempts

    def analyze_metrics(self) -> Dict:
        """Analyze all recorded attempts and calculate metrics."""
        attempts = self.read_recovery_attempts()

        if not attempts:
            return {
                "status": "no_data",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Basic stats
        total_attempts = len(attempts)
        successful = sum(1 for a in attempts if a.get("success", False))
        recovery_rate = (successful / total_attempts * 100) if total_attempts else 0

        # Pattern analysis
        patterns = defaultdict(lambda: {"count": 0, "successes": 0, "delays": []})
        for attempt in attempts:
            pattern = attempt.get("pattern_id", "unknown")
            patterns[pattern]["count"] += 1
            if attempt.get("success"):
                patterns[pattern]["successes"] += 1
            if "delay_sec" in attempt:
                patterns[pattern]["delays"].append(attempt["delay_sec"])

        # Calculate per-pattern stats
        pattern_stats = {}
        for pattern_id, data in patterns.items():
            success_rate = (
                (data["successes"] / data["count"] * 100) if data["count"] else 0
            )
            mttr = (
                statistics.mean(data["delays"])
                if data["delays"]
                else 0
            )
            pattern_stats[pattern_id] = {
                "total_attempts": data["count"],
                "successful_recoveries": data["successes"],
                "recovery_rate_pct": round(success_rate, 1),
                "mttr_seconds": round(mttr, 1),
            }

        # Calculate overall MTTR
        all_delays = [
            a.get("delay_sec", 0)
            for a in attempts
            if a.get("success")
        ]
        overall_mttr = statistics.mean(all_delays) if all_delays else 0

        # Severity analysis
        severity_counts = defaultdict(int)
        for attempt in attempts:
            severity = attempt.get("severity", "unknown")
            severity_counts[severity] += 1

        # Time-series for trend
        hourly_stats = self._analyze_hourly_trends(attempts)

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_attempts": total_attempts,
                "successful_recoveries": successful,
                "failed_recoveries": total_attempts - successful,
                "overall_recovery_rate_pct": round(recovery_rate, 1),
                "overall_mttr_seconds": round(overall_mttr, 1),
                "unique_patterns": len(patterns),
                "data_collection_period_days": self._get_collection_period_days(attempts),
            },
            "per_pattern": pattern_stats,
            "severity_distribution": dict(severity_counts),
            "hourly_trends": hourly_stats,
            "health": self._calculate_health_score(recovery_rate, overall_mttr),
        }

        return metrics

    def _analyze_hourly_trends(self, attempts: List[Dict]) -> Dict:
        """Analyze hourly recovery trends."""
        if not attempts:
            return {}

        hourly = defaultdict(lambda: {"count": 0, "successes": 0})

        for attempt in attempts:
            if "timestamp" in attempt:
                try:
                    dt = datetime.fromisoformat(attempt["timestamp"].replace("Z", "+00:00"))
                    hour_key = dt.strftime("%Y-%m-%d %H:00")
                    hourly[hour_key]["count"] += 1
                    if attempt.get("success"):
                        hourly[hour_key]["successes"] += 1
                except (ValueError, AttributeError):
                    pass

        return {
            k: {
                "total": v["count"],
                "successful": v["successes"],
                "rate_pct": round(
                    (v["successes"] / v["count"] * 100) if v["count"] else 0, 1
                ),
            }
            for k, v in sorted(hourly.items())
        }

    def _calculate_health_score(self, recovery_rate: float, mttr: float) -> Dict:
        """Calculate CI health score (0-100) based on recovery metrics."""
        # Recovery rate contribution (0-50 points)
        rate_score = min(50, (recovery_rate / 100) * 50)

        # MTTR contribution (0-50 points)
        # Target: < 30 seconds = full points
        # > 300 seconds = 0 points
        if mttr <= 30:
            mttr_score = 50
        elif mttr >= 300:
            mttr_score = 0
        else:
            mttr_score = 50 * (1 - (mttr - 30) / 270)

        total_score = rate_score + mttr_score

        # Determine health status
        if total_score >= 80:
            status = "excellent"
        elif total_score >= 60:
            status = "good"
        elif total_score >= 40:
            status = "fair"
        else:
            status = "poor"

        return {
            "score": round(total_score, 1),
            "status": status,
            "recovery_rate_contribution": round(rate_score, 1),
            "mttr_contribution": round(mttr_score, 1),
        }

    def _get_collection_period_days(self, attempts: List[Dict]) -> float:
        """Calculate data collection period in days."""
        if len(attempts) < 2:
            return 0

        timestamps = []
        for attempt in attempts:
            if "timestamp" in attempt:
                try:
                    dt = datetime.fromisoformat(attempt["timestamp"].replace("Z", "+00:00"))
                    timestamps.append(dt)
                except (ValueError, AttributeError):
                    pass

        if len(timestamps) >= 2:
            first = min(timestamps)
            last = max(timestamps)
            return (last - first).total_seconds() / 86400
        return 0

    def save_metrics(self, metrics: Dict) -> Path:
        """Save metrics snapshot."""
        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
        return self.metrics_file

    def generate_dashboard(self) -> Dict:
        """Generate dashboard data for monitoring."""
        metrics = self.analyze_metrics()

        if metrics.get("status") == "no_data":
            return {
                "status": "no_data",
                "message": "No recovery attempts recorded yet",
            }

        # Get top patterns
        pattern_stats = metrics.get("per_pattern", {})
        top_patterns = sorted(
            pattern_stats.items(),
            key=lambda x: x[1]["total_attempts"],
            reverse=True,
        )[:5]

        # Get recent hourly trend
        hourly_trends = metrics.get("hourly_trends", {})
        recent_hours = list(sorted(hourly_trends.items())[-24:])

        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": metrics.get("summary", {}),
            "health": metrics.get("health", {}),
            "top_patterns": [
                {
                    "pattern_id": p[0],
                    "stats": p[1],
                }
                for p in top_patterns
            ],
            "recent_24h_trend": {
                k: v for k, v in recent_hours
            },
            "aais_impact": {
                "reliability_score_delta": self._estimate_reliability_delta(metrics),
                "mttr_reduction_pct": self._estimate_mttr_improvement(),
                "target_metrics": {
                    "min_recovery_rate_pct": 80,
                    "max_mttr_seconds": 60,
                },
            },
        }

        with open(self.dashboard_file, "w") as f:
            json.dump(dashboard, f, indent=2)

        return dashboard

    def _estimate_reliability_delta(self, metrics: Dict) -> float:
        """Estimate improvement to AAIS Reliability score."""
        # Baseline: 0 (no self-healing)
        # Current: recovery_rate * mttr_factor
        recovery_rate = metrics.get("summary", {}).get("overall_recovery_rate_pct", 0)
        mttr = metrics.get("summary", {}).get("overall_mttr_seconds", 300)

        # MTTR factor: good MTTR (30-60s) adds to reliability
        if mttr <= 30:
            mttr_factor = 1.0
        elif mttr <= 60:
            mttr_factor = 0.8
        elif mttr <= 120:
            mttr_factor = 0.6
        else:
            mttr_factor = 0.4

        # Estimated delta (0-7 points)
        delta = (recovery_rate / 100) * 7 * mttr_factor
        return round(min(7, delta), 1)

    def _estimate_mttr_improvement(self) -> float:
        """Estimate MTTR improvement percentage from baseline."""
        # Baseline MTTR (no self-healing): ~5-10 minutes (300-600s)
        # Current MTTR from metrics
        metrics = self.analyze_metrics()
        current_mttr = metrics.get("summary", {}).get("overall_mttr_seconds", 0)

        if current_mttr == 0:
            return 0

        baseline_mttr = 600  # 10 minutes
        improvement_pct = ((baseline_mttr - current_mttr) / baseline_mttr) * 100
        return round(max(0, min(100, improvement_pct)), 1)


class MetricsReporter:
    """Generate metrics reports for CI output."""

    @staticmethod
    def generate_markdown(metrics: Dict, dashboard: Dict) -> str:
        """Generate markdown report."""
        summary = metrics.get("summary", {})
        health = metrics.get("health", {})
        aais_impact = dashboard.get("aais_impact", {})

        report = f"""# Self-Healing CI Metrics Report

**Generated:** {datetime.utcnow().isoformat()}

## Summary

| Metric | Value |
|--------|-------|
| Total Attempts | {summary.get('total_attempts', 0)} |
| Successful Recoveries | {summary.get('successful_recoveries', 0)} |
| Recovery Rate | {summary.get('overall_recovery_rate_pct', 0):.1f}% |
| Mean Time to Recovery (MTTR) | {summary.get('overall_mttr_seconds', 0):.1f}s |
| Unique Failure Patterns | {summary.get('unique_patterns', 0)} |
| Data Collection Period | {summary.get('data_collection_period_days', 0):.1f} days |

## CI Health Score

**Score:** {health.get('score', 0):.1f}/100 ({health.get('status', 'unknown').upper()})

- Recovery Rate Contribution: {health.get('recovery_rate_contribution', 0):.1f}/50
- MTTR Contribution: {health.get('mttr_contribution', 0):.1f}/50

## AAIS Reliability Impact

- **Estimated Reliability Score Delta:** +{aais_impact.get('reliability_score_delta', 0):.1f} points
- **MTTR Improvement:** {aais_impact.get('mttr_reduction_pct', 0):.1f}% reduction vs baseline
- **Target Metrics:**
  - Minimum Recovery Rate: {aais_impact.get('target_metrics', {}).get('min_recovery_rate_pct', 80)}%
  - Maximum MTTR: {aais_impact.get('target_metrics', {}).get('max_mttr_seconds', 60)}s

## Top Failure Patterns

| Pattern | Attempts | Success Rate | MTTR |
|---------|----------|--------------|------|
"""

        for pattern_info in dashboard.get("top_patterns", []):
            pattern_id = pattern_info["pattern_id"]
            stats = pattern_info["stats"]
            report += f"| {pattern_id} | {stats['total_attempts']} | {stats['recovery_rate_pct']:.1f}% | {stats['mttr_seconds']:.1f}s |\n"

        report += "\n## Recent 24-Hour Trend\n\n"
        report += "| Hour | Total | Successful | Rate |\n"
        report += "|------|-------|------------|------|\n"

        for hour, trend in list(dashboard.get("recent_24h_trend", {}).items())[-24:]:
            report += f"| {hour} | {trend['total']} | {trend['successful']} | {trend['rate_pct']:.1f}% |\n"

        return report

    @staticmethod
    def post_github_output(metrics: Dict, dashboard: Dict) -> None:
        """Post metrics to GitHub Actions output."""
        summary = metrics.get("summary", {})
        health = metrics.get("health", {})
        aais_impact = dashboard.get("aais_impact", {})

        output_file = os.environ.get("GITHUB_OUTPUT", "/dev/null")

        with open(output_file, "a") as f:
            f.write(f"recovery_rate={summary.get('overall_recovery_rate_pct', 0)}\n")
            f.write(f"mttr_seconds={summary.get('overall_mttr_seconds', 0)}\n")
            f.write(f"health_score={health.get('score', 0)}\n")
            f.write(
                f"reliability_delta={aais_impact.get('reliability_score_delta', 0)}\n"
            )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Telemetry collection and reporting")
    parser.add_argument(
        "--record",
        type=str,
        help="Record recovery attempt (JSON file)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze metrics and generate dashboard",
    )
    parser.add_argument(
        "--report",
        choices=["markdown", "json"],
        help="Generate report in specified format",
    )
    parser.add_argument(
        "--data-dir",
        default=".codex/telemetry",
        help="Telemetry data directory",
    )

    args = parser.parse_args()

    collector = TelemetryCollector(args.data_dir)

    if args.record:
        with open(args.record, "r") as f:
            attempt = json.load(f)
        collector.record_recovery_attempt(attempt)
        print(f"Recorded recovery attempt from {args.record}")

    if args.analyze:
        metrics = collector.analyze_metrics()
        collector.save_metrics(metrics)

        dashboard = collector.generate_dashboard()

        if args.report == "markdown":
            report = MetricsReporter.generate_markdown(metrics, dashboard)
            print(report)
        elif args.report == "json":
            print(json.dumps(dashboard, indent=2))
        else:
            print(f"Recovery Rate: {metrics['summary']['overall_recovery_rate_pct']:.1f}%")
            print(f"MTTR: {metrics['summary']['overall_mttr_seconds']:.1f}s")
            print(
                f"Health Score: {dashboard['health']['score']:.1f}/100 ({dashboard['health']['status']})"
            )

        # Post to GitHub output
        MetricsReporter.post_github_output(metrics, dashboard)


if __name__ == "__main__":
    main()
