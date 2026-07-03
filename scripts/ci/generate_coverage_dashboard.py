#!/usr/bin/env python3
"""
Coverage Dashboard Generator - Phase 3 Deliverable

Auto-generates `.codex/coverage/COVERAGE_DASHBOARD.md` from CI outputs.

Inputs:
  - .codex/coverage/BASELINE_TRACKING_REPORT.json
  - .codex/coverage/MODULE_BASELINE_MATRIX.json
  - .codex/coverage/BASELINE_HISTORY.ndjson

Outputs:
  - .codex/coverage/COVERAGE_DASHBOARD.md (auto-generated markdown dashboard)

Usage:
  python scripts/ci/generate_coverage_dashboard.py [--output <path>] [--input-dir <dir>]

  By default:
    - Reads from .codex/coverage/
    - Writes to .codex/coverage/COVERAGE_DASHBOARD.md
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse


def load_baseline_tracking(input_dir: Path) -> Dict[str, Any]:
    """Load BASELINE_TRACKING_REPORT.json"""
    report_path = input_dir / "BASELINE_TRACKING_REPORT.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Missing {report_path}")

    with open(report_path) as f:
        return json.load(f)


def load_module_matrix(input_dir: Path) -> Dict[str, Any]:
    """Load MODULE_BASELINE_MATRIX.json"""
    matrix_path = input_dir / "MODULE_BASELINE_MATRIX.json"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Missing {matrix_path}")

    with open(matrix_path) as f:
        return json.load(f)


def load_baseline_history(input_dir: Path) -> List[Dict[str, Any]]:
    """Load BASELINE_HISTORY.ndjson and return recent entries"""
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

    # Return last 30 entries for 30-day trend
    return entries[-30:] if entries else []


def get_trend_indicator(current: float, baseline: float) -> str:
    """Return trend indicator emoji"""
    diff = current - baseline
    if abs(diff) < 0.1:
        return "↔️ STABLE"
    elif diff > 0:
        return "↗️ INCREASING"
    else:
        return "↘️ DECREASING"


def get_status_color(status: str) -> str:
    """Map status to emoji"""
    status_map = {
        "STABLE": "🟢",
        "ACCEPTABLE": "🟡",
        "REGRESSION": "🔴",
        "ANOMALY": "🔴",
        "WARN": "🟡"
    }
    return status_map.get(status, "⚪")


def extract_tier_data(matrix: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract tier-level coverage from module matrix"""
    tiers = {}

    for key, value in matrix.items():
        if key.startswith("tier_") and isinstance(value, dict):
            tier_name = value.get("tier_name", key)
            status = value.get("status", "UNKNOWN")
            target = value.get("target_coverage", 0)
            modules = value.get("modules", [])

            # Calculate average coverage for this tier
            if modules:
                avg_coverage = sum(m.get("coverage_percent", 0) for m in modules) / len(modules)
            else:
                avg_coverage = 0

            test_count = value.get("total_tests", 0)

            tiers[key] = {
                "name": tier_name,
                "status": status,
                "target": target,
                "avg_coverage": avg_coverage,
                "module_count": len(modules),
                "test_count": test_count,
                "modules": modules
            }

    return tiers


def get_top_uncovered_modules(matrix: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    """Extract top 10 uncovered modules across all tiers"""
    all_modules = []

    for key, value in matrix.items():
        if key.startswith("tier_") and isinstance(value, dict):
            modules = value.get("modules", [])
            all_modules.extend(modules)

    # Sort by coverage (lowest first) and get top 10
    sorted_modules = sorted(all_modules, key=lambda m: m.get("coverage_percent", 0))
    return sorted_modules[:limit]


def calculate_30day_trend(history: List[Dict[str, Any]]) -> tuple[List[str], List[float]]:
    """Calculate 30-day rolling trend data"""
    if not history:
        return [], []

    # Get daily averages from NDJSON entries
    dates = []
    coverages = []

    current_date = None
    current_values = []

    for entry in history:
        ts = entry.get("timestamp", "")
        if ts:
            date = ts.split("T")[0]  # Extract date part
            coverage = entry.get("coverage", 0)

            if date != current_date:
                if current_values:
                    avg_coverage = sum(current_values) / len(current_values)
                    dates.append(current_date)
                    coverages.append(avg_coverage)

                current_date = date
                current_values = [coverage]
            else:
                current_values.append(coverage)

    # Add last day
    if current_values and current_date:
        avg_coverage = sum(current_values) / len(current_values)
        dates.append(current_date)
        coverages.append(avg_coverage)

    return dates, coverages


def generate_trend_table(dates: List[str], coverages: List[float]) -> str:
    """Generate markdown table for 30-day trend"""
    if not dates:
        return "No historical data available yet.\n"

    # Create table with ~7 day intervals for readability
    step = max(1, len(dates) // 5)

    table_rows = ["| Date | Coverage | Trend |"]
    table_rows.append("|------|----------|-------|")

    for i in range(0, len(dates), step):
        date = dates[i]
        coverage = coverages[i]

        # Calculate trend vs previous
        if i > 0:
            prev_coverage = coverages[i - 1]
            diff = coverage - prev_coverage
            if abs(diff) < 0.1:
                trend = "↔️"
            elif diff > 0:
                trend = f"↗️ +{diff:.2f}%"
            else:
                trend = f"↘️ {diff:.2f}%"
        else:
            trend = "📊 baseline"

        table_rows.append(f"| {date} | {coverage:.2f}% | {trend} |")

    return "\n".join(table_rows) + "\n"


def generate_dashboard(
    input_dir: Path,
    output_path: Path,
    baseline_tracking: Dict[str, Any],
    module_matrix: Dict[str, Any],
    baseline_history: List[Dict[str, Any]]
) -> None:
    """Generate the coverage dashboard markdown"""

    # Extract key metrics
    baseline = baseline_tracking.get("baseline_snapshot", {})
    current = baseline_tracking.get("current_metrics", {})
    validation = baseline_tracking.get("validation", {})
    quality = baseline_tracking.get("quality_metrics", {})
    status_indicators = baseline_tracking.get("status_indicators", {})

    baseline_coverage = baseline.get("baseline_coverage", 0)
    current_coverage = current.get("line_coverage_percent", 0)
    phase = baseline.get("phase", "UNKNOWN")
    variance = validation.get("variance_pct", 0)
    status = validation.get("status", "UNKNOWN")

    # Extract tier data
    tiers = extract_tier_data(module_matrix)

    # Get uncovered modules
    uncovered = get_top_uncovered_modules(module_matrix, limit=10)

    # Calculate 30-day trend
    dates, coverages = calculate_30day_trend(baseline_history)

    # Get timestamp
    from datetime import timezone
    now = datetime.now(timezone.utc)
    last_run = baseline_tracking.get("timestamp", now.isoformat())

    # Calculate phase progress
    target_coverage = 95.0
    progress_pct = (current_coverage / target_coverage) * 100

    # Build dashboard markdown
    dashboard = []

    dashboard.append("# 📊 Coverage Dashboard\n")
    dashboard.append(f"**Last Updated:** {last_run} (UTC)")
    dashboard.append(f"**Generated:** {now.isoformat()}Z (UTC)\n")

    # Section: Current Coverage
    dashboard.append("## 🎯 Current Coverage\n")
    status_emoji = get_status_color(status)
    trend = get_trend_indicator(current_coverage, baseline_coverage)

    dashboard.append("```")
    dashboard.append(f"Coverage: {current_coverage:.2f}%  {status_emoji} {status}  {trend}")
    dashboard.append(f"Baseline: {baseline_coverage:.2f}%")
    dashboard.append(f"Variance: {variance:+.2f}%")
    dashboard.append("```\n")

    # Target progress
    dashboard.append("## 📈 Phase Progress\n")
    dashboard.append("```")
    dashboard.append(f"Phase:              {phase}")
    dashboard.append("Target Coverage:    95.0%")
    dashboard.append(f"Current Coverage:   {current_coverage:.2f}%")
    dashboard.append(f"Progress:           {progress_pct:.1f}% toward target")
    dashboard.append(f"Status:             {'🔒 LOCKED - Monitoring' if phase == 'BASELINE_PHASE' else '🔓 Open - Incremental'}")
    dashboard.append("```\n")

    # Section: Quality Metrics
    dashboard.append("## ✅ Quality Metrics\n")
    dashboard.append("| Metric | Value | Status |")
    dashboard.append("|--------|-------|--------|")
    dashboard.append(f"| Test Pass Rate | {quality.get('test_pass_rate', 0):.1f}% | {'✅' if quality.get('test_pass_rate', 0) >= 99.5 else '⚠️'} |")
    dashboard.append(f"| Test Flakiness | {quality.get('test_flakiness', 0):.1f}% | {'✅' if quality.get('test_flakiness', 0) == 0 else '⚠️'} |")
    dashboard.append(f"| Test Determinism | {quality.get('test_determinism', 0):.1f}% | {'✅' if quality.get('test_determinism', 0) >= 99.5 else '⚠️'} |")
    dashboard.append(f"| Test Isolation | {quality.get('test_isolation', 0):.1f}% | {'✅' if quality.get('test_isolation', 0) >= 99.5 else '⚠️'} |\n")

    # Section: Module Tier Breakdown
    dashboard.append("## 📦 Module Tier Breakdown\n")

    for tier_key in sorted(tiers.keys()):
        tier = tiers[tier_key]
        emoji = get_status_color(tier["status"])

        dashboard.append(f"### {emoji} {tier['name']}\n")
        dashboard.append("```")
        dashboard.append(f"Target Coverage: {tier['target']:.1f}%")
        dashboard.append(f"Avg Coverage:    {tier['avg_coverage']:.1f}%")
        dashboard.append(f"Modules:         {tier['module_count']}")
        dashboard.append(f"Tests:           {tier['test_count']}")
        dashboard.append(f"Status:          {tier['status']}")
        dashboard.append("```\n")

        # Top modules in this tier
        modules = tier["modules"]
        if modules:
            dashboard.append("**Top 3 Modules:**")
            for module in modules[:3]:
                mod_name = module.get("module", "unknown")
                mod_cov = module.get("coverage_percent", 0)
                mod_tests = module.get("tests", 0)
                mod_status = module.get("status", "STABLE")
                dashboard.append(f"- {mod_name}: {mod_cov:.1f}% ({mod_tests} tests) {get_status_color(mod_status)}")
            dashboard.append("")

    # Section: Lowest Coverage Modules (Top 10 Uncovered)
    dashboard.append("## ⚠️ Top 10 Lowest Coverage Modules\n")
    dashboard.append("| Module | Coverage | Tests | Needed Lines |")
    dashboard.append("|--------|----------|-------|--------------|")

    for module in uncovered:
        mod_name = module.get("module", "unknown")
        mod_cov = module.get("coverage_percent", 0)
        mod_tests = module.get("tests", 0)
        # Estimate uncovered lines (rough: 100 lines per module assumed)
        estimated_lines = int((100 - mod_cov) * 1)  # Simplified estimate
        dashboard.append(f"| {mod_name} | {mod_cov:.1f}% | {mod_tests} | ~{estimated_lines} |")

    dashboard.append("")

    # Section: Validation Results
    dashboard.append("## 🔍 Latest Validation\n")
    passed = validation.get("passed", False)
    passed_emoji = "✅" if passed else "❌"
    message = validation.get("message", "No validation message")

    dashboard.append(f"{passed_emoji} **Status:** {message}\n")
    dashboard.append(f"**Timestamp:** {last_run}\n")

    # Section: 30-day Trend
    dashboard.append("## 📉 30-Day Coverage Trend\n")
    dashboard.append(generate_trend_table(dates, coverages))

    # Section: Actions
    dashboard.append("## 🚀 Recommended Actions\n")

    recommended = baseline_tracking.get("recommended_action", "Continue monitoring")
    dashboard.append(f"- {recommended}\n")

    # Add context-specific recommendations
    if phase == "BASELINE_PHASE":
        dashboard.append("- **Phase Status:** Baseline Phase - Coverage is LOCKED for monitoring")
        dashboard.append("- **Next Step:** Maintain stability for 30 days before Phase 1 progression\n")

    if current_coverage < baseline_coverage - 1.5:
        dashboard.append("- ⚠️ **Alert:** Coverage drop detected - investigate regression\n")
    elif current_coverage > baseline_coverage + 1.5:
        dashboard.append("- ℹ️ **Info:** Coverage gain detected - excellent progress!\n")

    # Footer
    dashboard.append("---\n")
    dashboard.append("*Dashboard auto-generated by `scripts/ci/generate_coverage_dashboard.py`*")
    dashboard.append("*Reference: `.codex/COVERAGE_VALIDATION_CRITERIA.md` | `.codex/PHASE_VALIDATION_GATES.yaml`*")

    # Write to output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(dashboard))

    print(f"✅ Dashboard generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Coverage Dashboard")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(".codex/coverage"),
        help="Input directory containing tracking data (default: .codex/coverage)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/coverage/COVERAGE_DASHBOARD.md"),
        help="Output path for dashboard (default: .codex/coverage/COVERAGE_DASHBOARD.md)"
    )

    args = parser.parse_args()

    try:
        # Load data
        baseline_tracking = load_baseline_tracking(args.input_dir)
        module_matrix = load_module_matrix(args.input_dir)
        baseline_history = load_baseline_history(args.input_dir)

        # Generate dashboard
        generate_dashboard(
            args.input_dir,
            args.output,
            baseline_tracking,
            module_matrix,
            baseline_history
        )

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error generating dashboard: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
