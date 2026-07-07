#!/usr/bin/env python3
"""
Security Findings Trend Analyzer

Purpose:
    Analyzes historical security findings to identify trends, patterns, and
    remediation velocity. Generates trend reports in Markdown and JSON formats.

Usage:
    python scripts/ci/security_findings_trend_analyzer.py \
      --cache-dir .codex/security-cache \
      --output-md security-findings-trend-report.md \
      --output-json .codex/security-findings-trend-metrics.json

Environment Variables:
    GITHUB_REPOSITORY: Repository for context in report
"""

import json
import logging
import os
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TrendReport:
    """Comprehensive trend analysis report"""
    analysis_date: str
    runs_analyzed: int
    date_range: str
    total_findings_span: Tuple[int, int]  # (min, max)
    critical_trend: str
    high_trend: str
    remediation_velocity: Dict[str, Any]
    most_common_cwes: List[Tuple[str, int]]
    new_vs_resolved: Dict[str, int]
    recurring_issues: List[Dict[str, Any]]
    seven_day_summary: List[Dict[str, Any]]


class SecurityFindingsTrendAnalyzer:
    """Analyzes security findings trends from cached runs"""

    def __init__(self, cache_dir: Path = Path(".codex/security-cache")):
        self.cache_dir = cache_dir
        self.runs_dir = cache_dir / "runs"
        self.index_file = cache_dir / "index.json"

    def analyze(self) -> Optional[TrendReport]:
        """
        Perform comprehensive trend analysis.

        Returns:
            TrendReport object or None if insufficient data
        """
        try:
            with open(self.index_file) as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("No cache index found")
            return None

        runs = index.get("runs", [])
        if len(runs) < 2:
            logger.warning(f"Insufficient data: only {len(runs)} run(s)")
            return None

        # Parse run metadata
        run_list = self._parse_run_metadata(runs)
        if not run_list:
            return None

        # Compute statistics
        total_findings = [r["findings_count"] for r in run_list]
        critical_counts = [r["critical_count"] for r in run_list]
        high_counts = [r["high_count"] for r in run_list]

        # Determine trends
        critical_trend = self._determine_trend(critical_counts)
        high_trend = self._determine_trend(high_counts)

        # Analyze last 7 days
        seven_day_summary = self._analyze_seven_day_trend(run_list)

        # Compute remediation velocity
        remediation_velocity = self._compute_remediation_velocity(run_list)

        # Get most common CWEs
        most_common_cwes = self._get_most_common_cwes(runs[:10])

        # Analyze new vs resolved
        new_vs_resolved = self._analyze_new_vs_resolved(runs[:2])

        # Find recurring issues
        recurring_issues = self._find_recurring_issues(runs[:10])

        # Create report
        report = TrendReport(
            analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            runs_analyzed=len(run_list),
            date_range=f"{run_list[-1]['timestamp']} to {run_list[0]['timestamp']}",
            total_findings_span=(min(total_findings), max(total_findings)),
            critical_trend=critical_trend,
            high_trend=high_trend,
            remediation_velocity=remediation_velocity,
            most_common_cwes=most_common_cwes,
            new_vs_resolved=new_vs_resolved,
            recurring_issues=recurring_issues,
            seven_day_summary=seven_day_summary,
        )

        return report

    def _parse_run_metadata(self, runs: List[Dict]) -> List[Dict[str, Any]]:
        """Parse and validate run metadata"""
        parsed = []
        for run in runs:
            try:
                timestamp = datetime.fromisoformat(run["timestamp"].replace("Z", "+00:00"))
                parsed.append({
                    "run_id": run["run_id"],
                    "timestamp": run["timestamp"],
                    "datetime": timestamp,
                    "findings_count": run.get("findings_count", 0),
                    "critical_count": run.get("critical_count", 0),
                    "high_count": run.get("high_count", 0),
                    "medium_count": run.get("medium_count", 0),
                    "low_count": run.get("low_count", 0),
                })
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid run: {run.get('run_id')} - {e}")
                continue
        return sorted(parsed, key=lambda x: x["datetime"])

    def _determine_trend(self, counts: List[int]) -> str:
        """
        Determine trend direction.

        Returns:
            'increasing', 'decreasing', or 'stable'
        """
        if len(counts) < 2:
            return "insufficient_data"

        if not counts:
            return "no_data"

        # Compare last 3 vs previous 3 (or available)
        split_point = len(counts) // 2
        recent_avg = sum(counts[:split_point]) / split_point if split_point > 0 else counts[0]
        previous_avg = sum(counts[split_point:]) / (len(counts) - split_point) if split_point < len(counts) else counts[-1]

        if recent_avg > previous_avg * 1.1:
            return "🔴 increasing"
        elif recent_avg < previous_avg * 0.9:
            return "🟢 decreasing"
        else:
            return "🟡 stable"

    def _analyze_seven_day_trend(
        self, run_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze last 7 days of findings"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent_runs = [r for r in run_list if r["datetime"] >= cutoff]

        summary = []
        for run in sorted(recent_runs, key=lambda x: x["datetime"]):
            summary.append({
                "date": run["datetime"].strftime("%Y-%m-%d"),
                "findings": run["findings_count"],
                "critical": run["critical_count"],
                "high": run["high_count"],
            })

        return summary

    def _compute_remediation_velocity(
        self, run_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute remediation velocity metrics.

        Returns:
            Dictionary with remediation velocity statistics
        """
        if len(run_list) < 2:
            return {"status": "insufficient_data"}

        # Get date range
        oldest = run_list[-1]["datetime"]
        newest = run_list[0]["datetime"]
        days_span = (newest - oldest).days or 1

        # Calculate rate of change
        oldest_count = run_list[-1]["findings_count"]
        newest_count = run_list[0]["findings_count"]
        delta = newest_count - oldest_count
        rate_per_day = delta / days_span

        return {
            "oldest_count": oldest_count,
            "newest_count": newest_count,
            "delta": delta,
            "rate_per_day": round(rate_per_day, 2),
            "days_analyzed": days_span,
            "estimated_clearance_days": int(-delta / rate_per_day) if rate_per_day < 0 else None,
        }

    def _get_most_common_cwes(self, runs: List[Dict]) -> List[Tuple[str, int]]:
        """Get most common CWE IDs"""
        cwe_counts = Counter()

        for run in runs:
            cache_files = list(self.runs_dir.glob(f"run-{run['run_id']}-*.json"))
            if not cache_files:
                continue

            try:
                with open(cache_files[0]) as f:
                    cache_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue

            for finding in cache_data.get("findings", []):
                if cwe_id := finding.get("cwe_id"):
                    cwe_counts[cwe_id] += 1

        return cwe_counts.most_common(10)

    def _analyze_new_vs_resolved(self, runs: List[Dict]) -> Dict[str, int]:
        """Analyze new vs resolved findings between last two runs"""
        if len(runs) < 2:
            return {"new": 0, "resolved": 0, "unchanged": 0}

        current_findings = self._get_findings_by_hash(runs[0]["run_id"])
        previous_findings = self._get_findings_by_hash(runs[1]["run_id"])

        current_hashes = set(current_findings.keys())
        previous_hashes = set(previous_findings.keys())

        new_count = len(current_hashes - previous_hashes)
        resolved_count = len(previous_hashes - current_hashes)
        unchanged_count = len(current_hashes & previous_hashes)

        return {
            "new": new_count,
            "resolved": resolved_count,
            "unchanged": unchanged_count,
        }

    def _get_findings_by_hash(self, run_id: str) -> Dict[str, Dict[str, Any]]:
        """Load findings indexed by hash"""
        cache_files = list(self.runs_dir.glob(f"run-{run_id}-*.json"))
        if not cache_files:
            return {}

        try:
            with open(cache_files[0]) as f:
                cache_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

        findings_by_hash = {}
        for finding in cache_data.get("findings", []):
            # Simple hash based on key fields
            key = f"{finding.get('tool')}|{finding.get('cwe_id')}|{finding.get('file')}"
            findings_by_hash[key] = finding

        return findings_by_hash

    def _find_recurring_issues(self, runs: List[Dict]) -> List[Dict[str, Any]]:
        """Find issues that recur across multiple runs"""
        finding_occurrences = defaultdict(list)

        for run in runs:
            cache_files = list(self.runs_dir.glob(f"run-{run['run_id']}-*.json"))
            if not cache_files:
                continue

            try:
                with open(cache_files[0]) as f:
                    cache_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue

            for finding in cache_data.get("findings", []):
                key = (
                    finding.get("cwe_id"),
                    finding.get("file"),
                    finding.get("severity"),
                )
                finding_occurrences[key].append(run["run_id"])

        # Find recurring (appears in 2+ runs)
        recurring = [
            {
                "cwe_id": key[0],
                "file": key[1],
                "severity": key[2],
                "occurrence_count": len(run_ids),
                "first_seen_in_runs": len(run_ids),
            }
            for key, run_ids in finding_occurrences.items()
            if len(run_ids) >= 2
        ]

        return sorted(recurring, key=lambda x: x["occurrence_count"], reverse=True)[:10]

    def generate_markdown_report(self, report: TrendReport) -> str:
        """Generate markdown report"""
        lines = [
            "# 📊 Security Findings Trend Analysis Report",
            "",
            f"**Analysis Date**: {report.analysis_date}",
            f"**Repository**: {os.getenv('GITHUB_REPOSITORY', 'Unknown')}",
            f"**Runs Analyzed**: {report.runs_analyzed}",
            f"**Date Range**: {report.date_range}",
            "",
            "## 📈 Overall Trend",
            "",
            "| Metric | Trend | Status |",
            "|--------|-------|--------|",
            f"| **CRITICAL** | {report.critical_trend} | {'🔴 Action Required' if 'increasing' in report.critical_trend else '✅ Improving'} |",
            f"| **HIGH** | {report.high_trend} | {'⚠️ Review' if 'increasing' in report.high_trend else '✅ Improving'} |",
            f"| **Total Findings** | {report.total_findings_span[0]} → {report.total_findings_span[1]} | {'+' if report.total_findings_span[1] > report.total_findings_span[0] else '-'} |",
            "",
            "## 🔧 Remediation Velocity",
            "",
        ]

        velocity = report.remediation_velocity
        if velocity.get("status") == "insufficient_data":
            lines.append("Insufficient historical data for velocity calculation.")
        else:
            lines.extend([
                f"- **Period**: {velocity.get('days_analyzed', 0)} days",
                f"- **Delta**: {velocity.get('delta', 0):+d} findings",
                f"- **Rate**: {velocity.get('rate_per_day', 0):+.2f} findings/day",
            ])
            if velocity.get("estimated_clearance_days"):
                lines.append(
                    f"- **Estimated Clearance**: {velocity['estimated_clearance_days']} days at current rate"
                )

        lines.extend([
            "",
            "## 🎯 Most Common Issues",
            "",
        ])

        if report.most_common_cwes:
            for cwe_id, count in report.most_common_cwes[:5]:
                lines.append(f"- **{cwe_id}**: {count} occurrences")
        else:
            lines.append("No CWE data available.")

        lines.extend([
            "",
            "## 📊 New vs Resolved (Last Run)",
            "",
            f"- **New**: {report.new_vs_resolved.get('new', 0)}",
            f"- **Resolved**: {report.new_vs_resolved.get('resolved', 0)}",
            f"- **Unchanged**: {report.new_vs_resolved.get('unchanged', 0)}",
            "",
            "## 🔄 Recurring Issues",
            "",
        ])

        if report.recurring_issues:
            for issue in report.recurring_issues[:5]:
                lines.append(
                    f"- **{issue.get('cwe_id', 'Unknown')}** in {issue.get('file', 'unknown')}: "
                    f"Found {issue.get('occurrence_count', 0)} times"
                )
        else:
            lines.append("No recurring issues detected.")

        lines.extend([
            "",
            "## 📅 Last 7 Days Summary",
            "",
        ])

        if report.seven_day_summary:
            lines.append("| Date | Total | CRITICAL | HIGH |")
            lines.append("|------|-------|----------|------|")
            for day in report.seven_day_summary:
                lines.append(
                    f"| {day.get('date')} | {day.get('findings', 0)} | "
                    f"{day.get('critical', 0)} | {day.get('high', 0)} |"
                )
        else:
            lines.append("Insufficient data for 7-day analysis.")

        lines.extend([
            "",
            "---",
            f"*Generated: {report.analysis_date}*",
        ])

        return "\n".join(lines)

    def _generate_ascii_bar_chart(
        self, data: List[Tuple[str, int]], max_width: int = 50, label: str = "Value"
    ) -> str:
        """Generate ASCII bar chart from data"""
        if not data:
            return "(No data)"

        max_value = max(v for _, v in data) if data else 1
        if max_value == 0:
            max_value = 1

        lines = []
        for label_text, value in data:
            bar_width = int((value / max_value) * max_width) if max_value > 0 else 0
            bar = "█" * bar_width
            lines.append(f"  {label_text:<20} │ {bar:<{max_width}} {value:>5}")

        return "\n".join(lines)

    def _generate_severity_distribution(self, run_list: List[Dict[str, Any]]) -> str:
        """Generate severity distribution ASCII chart"""
        if not run_list:
            return "(No data)"

        # Get latest run
        latest_run = run_list[0]

        total = latest_run.get("findings_count", 1) or 1
        critical = latest_run.get("critical_count", 0)
        high = latest_run.get("high_count", 0)
        medium = latest_run.get("medium_count", 0)
        low = latest_run.get("low_count", 0)

        # Calculate percentages
        critical_pct = (critical / total * 100) if total > 0 else 0
        high_pct = (high / total * 100) if total > 0 else 0
        medium_pct = (medium / total * 100) if total > 0 else 0
        low_pct = (low / total * 100) if total > 0 else 0

        lines = [
            "  CRITICAL │ 🔴 " + "█" * int(critical_pct / 2) + f" {critical_pct:5.1f}% ({critical})",
            "  HIGH     │ 🟠 " + "█" * int(high_pct / 2) + f" {high_pct:5.1f}% ({high})",
            "  MEDIUM   │ 🟡 " + "█" * int(medium_pct / 2) + f" {medium_pct:5.1f}% ({medium})",
            "  LOW      │ 🟢 " + "█" * int(low_pct / 2) + f" {low_pct:5.1f}% ({low})",
        ]

        return "\n".join(lines)

    def _generate_trend_sparkline(self, counts: List[int], width: int = 30) -> str:
        """Generate a simple trend sparkline"""
        if not counts or len(counts) == 0:
            return "(No data)"

        if len(counts) == 1:
            return f"  Single data point: {counts[0]}"

        # Select up to `width` data points
        step = max(1, len(counts) // width)
        sampled = counts[::step]

        if not sampled:
            return "(Insufficient data)"

        min_val = min(sampled)
        max_val = max(sampled)

        if min_val == max_val:
            return f"  Stable at {min_val}"

        # Create sparkline characters
        sparkchars = "▁▂▃▄▅▆▇█"
        sparkline = ""
        for val in sampled:
            normalized = int((val - min_val) / (max_val - min_val) * (len(sparkchars) - 1))
            sparkline += sparkchars[min(normalized, len(sparkchars) - 1)]

        return f"  {sparkline} (range: {min_val} → {max_val})"

    def generate_dashboard_markdown(
        self, cache_dir: Path, output_path: Path
    ) -> Optional[str]:
        """
        Generate comprehensive dashboard markdown.

        Args:
            cache_dir: Path to cache directory
            output_path: Path to write dashboard markdown

        Returns:
            Dashboard markdown content or None on error
        """
        try:
            with open(cache_dir / "index.json") as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("No cache index found for dashboard generation")
            return None

        runs = index.get("runs", [])
        if not runs:
            logger.warning("No cached runs available for dashboard")
            return None

        # Parse run metadata
        run_list = self._parse_run_metadata(runs)
        if not run_list:
            return None

        # Generate dashboard sections
        lines = [
            "# 🛡️ Security Findings Dashboard",
            "",
            f"**Last Updated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Repository**: {os.getenv('GITHUB_REPOSITORY', 'Unknown')}",
            f"**Cached Runs**: {len(run_list)}",
            "",
            "---",
            "",
            "## 📊 Summary Stats",
            "",
        ]

        # Current stats from latest run
        latest = run_list[0]
        lines.extend([
            f"- **Total Findings** (latest): {latest['findings_count']}",
            f"- **CRITICAL**: {latest['critical_count']}",
            f"- **HIGH**: {latest['high_count']}",
            f"- **MEDIUM**: {latest['medium_count']}",
            f"- **LOW**: {latest['low_count']}",
            "",
        ])

        # 7-day trend
        lines.extend([
            "## 📈 7-Day Trend (Total Findings)",
            "",
        ])

        cutoff_7d = datetime.now(timezone.utc) - timedelta(days=7)
        recent_7d = [r for r in run_list if r["datetime"] >= cutoff_7d]

        if recent_7d:
            findings_7d = [r["findings_count"] for r in sorted(recent_7d, key=lambda x: x["datetime"])]
            lines.append("```")
            lines.append(self._generate_trend_sparkline(findings_7d, width=30))
            lines.append("```")
        else:
            lines.append("(Insufficient data for 7-day trend)")

        lines.append("")

        # 30-day trend
        lines.extend([
            "## 📅 30-Day Trend (Total Findings)",
            "",
        ])

        cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
        recent_30d = [r for r in run_list if r["datetime"] >= cutoff_30d]

        if recent_30d:
            findings_30d = [r["findings_count"] for r in sorted(recent_30d, key=lambda x: x["datetime"])]
            lines.append("```")
            lines.append(self._generate_trend_sparkline(findings_30d, width=50))
            lines.append("```")
        else:
            lines.append("(Insufficient data for 30-day trend)")

        lines.append("")

        # Severity distribution
        lines.extend([
            "## 🎯 Current Severity Distribution",
            "",
            "```",
        ])
        lines.append(self._generate_severity_distribution(run_list))
        lines.extend([
            "```",
            "",
        ])

        # Top 5 recurring issues
        lines.extend([
            "## 🔄 Top 5 Recurring Issues (All Runs)",
            "",
        ])

        recurring_issues = self._find_recurring_issues(runs[:10])
        if recurring_issues:
            for i, issue in enumerate(recurring_issues[:5], 1):
                lines.append(
                    f"{i}. **{issue.get('cwe_id', 'Unknown')}** in `{issue.get('file', 'unknown')}`  "
                    f"({issue.get('severity', 'N/A')}) — {issue.get('occurrence_count', 0)} occurrences"
                )
        else:
            lines.append("No recurring issues detected.")

        lines.append("")

        # Remediation velocity
        lines.extend([
            "## 🚀 Remediation Velocity",
            "",
        ])

        remediation_velocity = self._compute_remediation_velocity(run_list)
        if remediation_velocity.get("status") == "insufficient_data":
            lines.append("Insufficient data for velocity calculation.")
        else:
            velocity = remediation_velocity
            lines.extend([
                f"- **Analysis Period**: {velocity.get('days_analyzed', 0)} days",
                f"- **Finding Delta**: {velocity.get('delta', 0):+d}",
                f"- **Rate**: {velocity.get('rate_per_day', 0):+.2f} findings/day",
            ])
            if velocity.get("rate_per_day", 0) < 0:
                lines.append(
                    f"- **Estimated Clearance**: {velocity.get('estimated_clearance_days', 'N/A')} days at current rate"
                )
            else:
                lines.append("- **Trend**: ⚠️ Findings increasing")

        lines.extend([
            "",
            "## 📋 Top CWEs",
            "",
        ])

        most_common_cwes = self._get_most_common_cwes(runs[:10])
        if most_common_cwes:
            lines.append("```")
            cwe_data = [(f"{cwe[0]}", cwe[1]) for cwe in most_common_cwes[:5]]
            lines.append(self._generate_ascii_bar_chart(cwe_data, max_width=30, label="CWE"))
            lines.append("```")
        else:
            lines.append("No CWE data available.")

        lines.extend([
            "",
            "---",
            f"*Dashboard generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}*",
        ])

        dashboard_content = "\n".join(lines)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(dashboard_content)
        logger.info(f"✅ Dashboard generated: {output_path}")

        return dashboard_content


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Security Findings Trend Analyzer")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".codex/security-cache"),
        help="Cache directory",
    )
    parser.add_argument("--output-md", type=Path, help="Markdown report output file")
    parser.add_argument("--output-json", type=Path, help="JSON report output file")
    parser.add_argument(
        "--dashboard",
        type=Path,
        default=Path(".codex/security-findings-dashboard.md"),
        help="Dashboard markdown output file",
    )

    args = parser.parse_args()

    analyzer = SecurityFindingsTrendAnalyzer(args.cache_dir)

    # Generate trend analysis report
    report = analyzer.analyze()
    if report:
        # Generate markdown report
        if args.output_md:
            md_content = analyzer.generate_markdown_report(report)
            args.output_md.write_text(md_content)
            logger.info(f"✅ Markdown report: {args.output_md}")

        # Generate JSON report
        if args.output_json:
            args.output_json.write_text(json.dumps(asdict(report), indent=2, default=str))
            logger.info(f"✅ JSON report: {args.output_json}")
    else:
        logger.warning("No trend report generated (insufficient data)")

    # Generate dashboard (separate from report)
    dashboard_content = analyzer.generate_dashboard_markdown(args.cache_dir, args.dashboard)
    if dashboard_content:
        logger.info(f"✅ Dashboard: {args.dashboard}")
        return 0
    else:
        logger.warning("No dashboard generated (no cached runs)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
