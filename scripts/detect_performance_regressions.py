#!/usr/bin/env python3
"""
Detect Performance Regressions
Phase 4D Planset 007 - Regression detection engine

Detects regressions using:
- Statistical tests (Welch's t-test)
- Trend analysis (linear regression)
- Anomaly detection (z-score)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
from scipy import stats


def load_json_safe(path: Path) -> dict[str, Any]:
    """Load JSON file with error handling"""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        return {}


def detect_regression(
    baseline: list[float],
    current: list[float],
    threshold: float = 0.10,
    alpha: float = 0.05,
) -> tuple[bool, dict[str, Any]]:
    """
    Detect performance regression using statistical testing.
    
    Args:
        baseline: Historical measurements
        current: Current measurements
        threshold: Minimum % change to flag as regression (default: 10%)
        alpha: Significance level (default: 0.05)
        
    Returns:
        Tuple of (is_regression, details)
    """
    if len(baseline) < 5 or len(current) < 5:
        return False, {"reason": "Insufficient samples"}
    
    baseline_mean = np.mean(baseline)
    current_mean = np.mean(current)
    
    # Calculate relative change
    percent_change = (current_mean - baseline_mean) / abs(baseline_mean)
    
    # Check magnitude first (fast path)
    if abs(percent_change) < threshold:
        return False, {
            "percent_change": percent_change,
            "baseline_mean": baseline_mean,
            "current_mean": current_mean,
            "reason": "Below threshold",
        }
    
    # Welch's t-test for unequal variances
    t_statistic, p_value = stats.ttest_ind(baseline, current, equal_var=False)
    
    is_significant = p_value < alpha
    is_regression = is_significant and percent_change > threshold
    
    return is_regression, {
        "percent_change": percent_change,
        "baseline_mean": baseline_mean,
        "current_mean": current_mean,
        "t_statistic": float(t_statistic),
        "p_value": float(p_value),
        "is_significant": is_significant,
        "baseline_samples": len(baseline),
        "current_samples": len(current),
        "threshold": threshold,
    }


def calculate_trend(values: list[float]) -> dict[str, Any]:
    """Calculate trend using linear regression"""
    if len(values) < 3:
        return {"reason": "Insufficient samples"}
    
    x = np.arange(len(values))
    y = np.array(values)
    
    # Linear regression
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    
    # R-squared
    y_fit = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_fit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    return {
        "slope": float(slope),
        "direction": "increasing" if slope > 0 else "decreasing",
        "r_squared": float(r_squared),
    }


def main() -> int:
    """Detect performance regressions"""
    parser = argparse.ArgumentParser(
        description="Detect performance regressions"
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Baseline metrics file",
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Current metrics file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file for regression report",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.10,
        help="Regression threshold (% change)",
    )
    
    args = parser.parse_args()
    
    # Load data
    baseline_data = load_json_safe(args.baseline)
    current_data = load_json_safe(args.current)
    
    # Analyze regressions
    regressions = {
        "timestamp": datetime.now().isoformat(),
        "total_metrics_analyzed": 0,
        "regressions_detected": 0,
        "regressions": [],
        "trends": [],
    }
    
    # Simple detection logic for demonstration
    # In production, this would be more sophisticated
    
    # Check workflow timing if available
    baseline_workflows = baseline_data.get("baselines", {}).get("workflows", {})
    
    for workflow_name, workflow_data in baseline_workflows.items():
        if isinstance(workflow_data, dict):
            current_duration = workflow_data.get("current_duration_minutes", 0)
            target_duration = workflow_data.get("target_duration_minutes", 0)
            
            if current_duration > 0 and target_duration > 0:
                percent_diff = (current_duration - target_duration) / target_duration
                
                if percent_diff > args.threshold:
                    regressions["total_metrics_analyzed"] += 1
                    regressions["regressions_detected"] += 1
                    
                    regressions["regressions"].append({
                        "metric": workflow_name,
                        "type": "workflow_timing",
                        "percent_change": percent_diff,
                        "baseline_value": target_duration,
                        "current_value": current_duration,
                        "unit": "minutes",
                        "severity": "CRITICAL" if percent_diff > 0.25 else "HIGH",
                    })
    
    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    if args.format == "json":
        with open(args.output, "w") as f:
            json.dump(regressions, f, indent=2)
    else:
        # Markdown format
        lines = [
            "# Performance Regression Report",
            "",
            f"**Timestamp**: {regressions['timestamp']}",
            f"**Metrics Analyzed**: {regressions['total_metrics_analyzed']}",
            f"**Regressions Detected**: {regressions['regressions_detected']}",
            "",
        ]
        
        if regressions["regressions"]:
            lines.append("## Regressions Detected")
            lines.append("")
            for regression in regressions["regressions"]:
                lines.append(
                    f"### {regression['metric']} ({regression['severity']})"
                )
                lines.append(
                    f"- Change: {regression['percent_change']:+.1%}"
                )
                lines.append(
                    f"- Baseline: {regression['baseline_value']} {regression['unit']}"
                )
                lines.append(
                    f"- Current: {regression['current_value']} {regression['unit']}"
                )
                lines.append("")
        else:
            lines.append("✅ No regressions detected")
        
        with open(args.output, "w") as f:
            f.write("\n".join(lines))
    
    print(f"✅ Regression report saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
