#!/usr/bin/env python3
"""
Weekly Coverage Report Generator - Phase 3 Deliverable

Auto-generates `.codex/coverage/WEEKLY_COVERAGE_REPORT.md` from baseline history.

Inputs:
  - .codex/coverage/BASELINE_HISTORY.ndjson (historical tracking data)
  - .codex/coverage/BASELINE_TRACKING_REPORT.json (current snapshot)
  - .codex/coverage/MODULE_BASELINE_MATRIX.json (module tier breakdown)

Outputs:
  - .codex/coverage/WEEKLY_COVERAGE_REPORT.md (markdown report)

Usage:
  python scripts/ci/generate_weekly_report.py [--output <path>] [--weeks 1]

  By default generates report for the current week ending today.
  Use --weeks N to generate report for the last N weeks.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import argparse
from collections import defaultdict


def load_baseline_history(input_dir: Path) -> List[Dict[str, Any]]:
    """Load BASELINE_HISTORY.ndjson"""
    history_path = input_dir / "BASELINE_HISTORY.ndjson"
    if not history_path.exists():
        return []
    
    entries = []
    with open(history_path) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    return entries


def load_baseline_tracking(input_dir: Path) -> Dict[str, Any]:
    """Load BASELINE_TRACKING_REPORT.json"""
    report_path = input_dir / "BASELINE_TRACKING_REPORT.json"
    if not report_path.exists():
        return {}
    
    with open(report_path) as f:
        return json.load(f)


def load_module_matrix(input_dir: Path) -> Dict[str, Any]:
    """Load MODULE_BASELINE_MATRIX.json"""
    matrix_path = input_dir / "MODULE_BASELINE_MATRIX.json"
    if not matrix_path.exists():
        return {}
    
    with open(matrix_path) as f:
        return json.load(f)


def get_week_dates(weeks_ago: int = 0) -> Tuple[datetime, datetime]:
    """Get start and end dates for a given week
    
    weeks_ago=0 means current week (Mon-Sun)
    weeks_ago=1 means last week, etc.
    """
    from datetime import timezone
    today = datetime.now(timezone.utc)
    
    # Go back weeks_ago weeks plus get to start of that week (Monday)
    days_back = (today.weekday() + 7 * weeks_ago)
    week_start = today - timedelta(days=days_back)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    week_end = week_start + timedelta(days=7)
    
    return week_start, week_end


def filter_history_by_date_range(
    history: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """Filter history entries to a specific date range"""
    filtered = []
    
    for entry in history:
        ts_str = entry.get("timestamp", "")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if start_date <= ts < end_date:
                    filtered.append(entry)
            except (ValueError, AttributeError):
                pass
    
    return filtered


def calculate_week_stats(
    week_entries: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate statistics for a given week"""
    if not week_entries:
        return {
            "days_with_data": 0,
            "runs": 0,
            "avg_coverage": 0,
            "min_coverage": 0,
            "max_coverage": 0,
            "variance": 0,
            "trend": "no data"
        }
    
    coverages = [e.get("coverage", 0) for e in week_entries]
    
    daily_stats = defaultdict(list)
    for entry in week_entries:
        ts = entry.get("timestamp", "")
        if ts:
            date = ts.split("T")[0]
            daily_stats[date].append(entry.get("coverage", 0))
    
    daily_avg = [sum(v) / len(v) for v in daily_stats.values()]
    
    avg_cov = sum(coverages) / len(coverages) if coverages else 0
    min_cov = min(coverages) if coverages else 0
    max_cov = max(coverages) if coverages else 0
    variance = max_cov - min_cov
    
    # Determine trend
    if len(daily_avg) >= 2:
        first_half_avg = sum(daily_avg[:len(daily_avg)//2]) / (len(daily_avg)//2)
        second_half_avg = sum(daily_avg[len(daily_avg)//2:]) / (len(daily_avg) - len(daily_avg)//2)
        diff = second_half_avg - first_half_avg
        
        if abs(diff) < 0.1:
            trend = "↔️ STABLE"
        elif diff > 0:
            trend = f"↗️ +{diff:.2f}%"
        else:
            trend = f"↘️ {diff:.2f}%"
    else:
        trend = "insufficient data"
    
    return {
        "days_with_data": len(daily_stats),
        "runs": len(week_entries),
        "avg_coverage": avg_cov,
        "min_coverage": min_cov,
        "max_coverage": max_cov,
        "variance": variance,
        "trend": trend
    }


def extract_test_stats(
    week_entries: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Extract test-related statistics from week entries"""
    if not week_entries:
        return {
            "avg_pass_rate": 0,
            "avg_flakiness": 0,
            "avg_determinism": 0,
            "total_runs": 0
        }
    
    pass_rates = []
    flakiness_values = []
    determinism_values = []
    
    for entry in week_entries:
        # Look for quality metrics in baseline tracking embedded data
        # or separate quality_metrics field
        if "quality_metrics" in entry:
            qm = entry["quality_metrics"]
            pass_rates.append(qm.get("test_pass_rate", 100))
            flakiness_values.append(qm.get("test_flakiness", 0))
            determinism_values.append(qm.get("test_determinism", 100))
    
    return {
        "avg_pass_rate": sum(pass_rates) / len(pass_rates) if pass_rates else 0,
        "avg_flakiness": sum(flakiness_values) / len(flakiness_values) if flakiness_values else 0,
        "avg_determinism": sum(determinism_values) / len(determinism_values) if determinism_values else 0,
        "total_runs": len(week_entries)
    }


def compare_weeks(
    current_week: Dict[str, Any],
    previous_week: Dict[str, Any]
) -> Dict[str, Any]:
    """Compare current week to previous week"""
    if not previous_week.get("avg_coverage"):
        return {
            "coverage_change": 0,
            "coverage_direction": "baseline",
            "pass_rate_change": 0,
            "flakiness_change": 0
        }
    
    coverage_delta = current_week.get("avg_coverage", 0) - previous_week.get("avg_coverage", 0)
    pass_rate_delta = current_week.get("avg_pass_rate", 0) - previous_week.get("avg_pass_rate", 0)
    flakiness_delta = current_week.get("avg_flakiness", 0) - previous_week.get("avg_flakiness", 0)
    
    return {
        "coverage_change": coverage_delta,
        "coverage_direction": "↗️ up" if coverage_delta > 0 else "↘️ down" if coverage_delta < 0 else "↔️ stable",
        "pass_rate_change": pass_rate_delta,
        "flakiness_change": flakiness_delta
    }


def get_risks_and_alerts(
    current_stats: Dict[str, Any],
    current_quality: Dict[str, Any],
    current_tracking: Dict[str, Any]
) -> List[str]:
    """Identify risks and generate alerts"""
    risks = []
    
    # Coverage risks
    if current_stats.get("variance", 0) > 1.5:
        risks.append("⚠️ High coverage variance detected (>1.5%) - investigate stability")
    
    # Quality risks
    if current_quality.get("avg_flakiness", 0) > 0.5:
        risks.append("⚠️ Test flakiness detected - trigger autonomous-test-healer-agent")
    
    if current_quality.get("avg_pass_rate", 100) < 99.5:
        risks.append("⚠️ Test pass rate below threshold (<99.5%)")
    
    if current_quality.get("avg_determinism", 100) < 99.5:
        risks.append("⚠️ Test determinism below target (<99.5%)")
    
    # Check for regressions from tracking data
    validation = current_tracking.get("validation", {})
    if not validation.get("passed", True):
        risks.append("❌ Latest validation FAILED - immediate investigation required")
    
    if not risks:
        risks.append("✅ No risks detected - all metrics within acceptable range")
    
    return risks


def generate_weekly_report(
    input_dir: Path,
    output_path: Path,
    weeks_back: int = 0
) -> None:
    """Generate weekly coverage report"""
    
    # Load data
    history = load_baseline_history(input_dir)
    current_tracking = load_baseline_tracking(input_dir)
    module_matrix = load_module_matrix(input_dir)
    
    # Get week boundaries
    week_start, week_end = get_week_dates(weeks_back)
    prev_week_start, prev_week_end = get_week_dates(weeks_back + 1)
    
    # Filter history
    current_week_entries = filter_history_by_date_range(history, week_start, week_end)
    previous_week_entries = filter_history_by_date_range(history, prev_week_start, prev_week_end)
    
    # Calculate stats
    current_stats = calculate_week_stats(current_week_entries)
    previous_stats = calculate_week_stats(previous_week_entries)
    
    current_quality = extract_test_stats(current_week_entries)
    previous_quality = extract_test_stats(previous_week_entries)
    
    week_comparison = compare_weeks(
        {**current_stats, **current_quality},
        {**previous_stats, **previous_quality}
    )
    
    # Extract tier data
    tier_data = {}
    for key, value in module_matrix.items():
        if key.startswith("tier_") and isinstance(value, dict):
            modules = value.get("modules", [])
            if modules:
                avg_coverage = sum(m.get("coverage_percent", 0) for m in modules) / len(modules)
                tier_data[key] = {
                    "name": value.get("tier_name", key),
                    "avg_coverage": avg_coverage,
                    "module_count": len(modules)
                }
    
    # Get risks
    risks = get_risks_and_alerts(current_stats, current_quality, current_tracking)
    
    # Build report
    report = []
    
    report.append("# 📊 Weekly Coverage Report\n")
    
    week_str = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
    report.append(f"**Period:** {week_str} (UTC)")
    
    from datetime import timezone
    now = datetime.now(timezone.utc)
    report.append(f"**Generated:** {now.isoformat()} (UTC)\n")
    
    # Section: Week-over-Week Change
    report.append("## 📈 Week-over-Week Change\n")
    
    if previous_stats.get("avg_coverage"):
        change = week_comparison.get("coverage_change", 0)
        direction = week_comparison.get("coverage_direction", "unknown")
        report.append(f"```")
        report.append(f"Coverage Change: {change:+.2f}%  {direction}")
        report.append(f"This Week:       {current_stats.get('avg_coverage', 0):.2f}%")
        report.append(f"Last Week:       {previous_stats.get('avg_coverage', 0):.2f}%")
        report.append(f"Variance:        {current_stats.get('variance', 0):.2f}%")
        report.append(f"```\n")
    else:
        report.append("*No previous week data available for comparison.*\n")
    
    # Section: Module Tier Performance
    report.append("## 📦 Module Tier Performance\n")
    report.append(f"| Tier | Coverage | Modules |")
    report.append(f"|------|----------|---------|")
    
    for tier_key in sorted(tier_data.keys()):
        tier = tier_data[tier_key]
        report.append(f"| {tier['name']} | {tier['avg_coverage']:.1f}% | {tier['module_count']} |")
    
    report.append("")
    
    # Section: Test Trends
    report.append("## 🧪 Test Trends\n")
    report.append(f"```")
    report.append(f"This Week:")
    report.append(f"  Pass Rate:    {current_quality.get('avg_pass_rate', 0):.1f}%")
    report.append(f"  Flakiness:    {current_quality.get('avg_flakiness', 0):.1f}%")
    report.append(f"  Determinism:  {current_quality.get('avg_determinism', 0):.1f}%")
    report.append(f"  Test Runs:    {current_quality.get('total_runs', 0)}")
    report.append(f"```\n")
    
    if previous_quality.get("total_runs"):
        report.append(f"vs. Last Week:")
        pass_delta = week_comparison.get("pass_rate_change", 0)
        flakiness_delta = week_comparison.get("flakiness_change", 0)
        report.append(f"- Pass Rate Change: {pass_delta:+.1f}%")
        report.append(f"- Flakiness Change: {flakiness_delta:+.1f}%\n")
    
    # Section: Risks & Alerts
    report.append("## 🚨 Risks & Alerts\n")
    
    for risk in risks:
        report.append(f"- {risk}")
    
    report.append("")
    
    # Section: Action Items
    report.append("## ✅ Action Items\n")
    
    if current_stats.get("variance", 0) > 1.5:
        report.append("- [ ] Investigate coverage variance - identify root cause")
    
    if current_quality.get("avg_flakiness", 0) > 0:
        report.append("- [ ] Run autonomous-test-healer-agent on flaky tests")
    
    if week_comparison.get("coverage_change", 0) < -1.0:
        report.append("- [ ] Coverage dropped significantly - review merged PRs")
    elif week_comparison.get("coverage_change", 0) > 0:
        report.append("- [ ] Excellent coverage progress - document approach for scaling")
    else:
        report.append("- [ ] Coverage stable - continue baseline monitoring")
    
    report.append("- [ ] Review tier-level progression for Phase 1 readiness\n")
    
    # Section: Next Phase Recommendations
    report.append("## 🎯 Phase Progression\n")
    
    baseline_cov = current_tracking.get("baseline_snapshot", {}).get("baseline_coverage", 34.63)
    phase = current_tracking.get("baseline_snapshot", {}).get("phase", "BASELINE_PHASE")
    
    if phase == "BASELINE_PHASE":
        report.append(f"**Current:** Baseline Phase @ {baseline_cov:.2f}%")
        report.append(f"**Next Phase:** Phase 1 (40% target) - Ready after 30 days of stability")
        report.append(f"**Prerequisite:** Coverage must remain {baseline_cov - 1.5:.2f}% - {baseline_cov + 1.5:.2f}% for {30} consecutive days\n")
    
    # Footer
    report.append("---\n")
    report.append(f"*Weekly report auto-generated by `scripts/ci/generate_weekly_report.py`*")
    report.append(f"*Reference: `.codex/COVERAGE_VALIDATION_CRITERIA.md` | `.codex/PHASE_VALIDATION_GATES.yaml`*")
    
    # Write to output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(report))
    
    print(f"✅ Weekly report generated: {output_path}")
    print(f"   Period: {week_str}")
    print(f"   Coverage: {current_stats.get('avg_coverage', 0):.2f}% (variance: {current_stats.get('variance', 0):.2f}%)")


def main():
    parser = argparse.ArgumentParser(description="Generate Weekly Coverage Report")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(".codex/coverage"),
        help="Input directory containing tracking data (default: .codex/coverage)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/coverage/WEEKLY_COVERAGE_REPORT.md"),
        help="Output path for report (default: .codex/coverage/WEEKLY_COVERAGE_REPORT.md)"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=0,
        help="Weeks back to generate report for (0=current week, 1=last week, etc.)"
    )
    
    args = parser.parse_args()
    
    try:
        generate_weekly_report(args.input_dir, args.output, args.weeks)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error generating weekly report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
