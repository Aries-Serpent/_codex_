#!/usr/bin/env python3
"""
Extract coverage metrics from coverage.json.

This script parses pytest-cov JSON output and creates a metrics file with:
- Overall coverage percentage
- Total/covered lines
- Branch coverage
- Status (above/below target)
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def extract_coverage(coverage_json_path: str, output_path: str) -> None:
    """Extract coverage metrics from coverage.json."""
    
    try:
        with open(coverage_json_path) as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        print(f"Coverage file not found: {coverage_json_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in coverage file: {coverage_json_path}")
        sys.exit(1)
    
    # Extract summary data
    summary = coverage_data.get('totals', {})
    
    coverage_percent = summary.get('percent_covered', 0.0)
    total_lines = summary.get('num_statements', 0)
    covered_lines = summary.get('covered_lines', 0)
    num_branches = summary.get('num_branches', 0)
    covered_branches = summary.get('covered_branches', 0)
    
    # Determine status
    target_coverage = 70.0
    if coverage_percent >= target_coverage:
        status = "above_target"
    elif coverage_percent >= 60.0:
        status = "approaching_target"
    else:
        status = "below_target"
    
    # Determine trend (simplified - no historical data in this script)
    trend = "stable"
    
    # Create metrics output
    metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "coverage_overall",
        "value": round(coverage_percent, 2),
        "unit": "%",
        "target": target_coverage,
        "status": status,
        "trend": trend,
        "data_points": {
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "branches": num_branches,
            "covered_branches": covered_branches,
        },
        "source": "pytest-cov",
        "workflow_run_id": None,  # Set by CI
        "commit_sha": None,  # Set by CI
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Coverage metrics written to {output_path}")
    print(f"   Coverage: {coverage_percent:.2f}% (target: {target_coverage}%)")
    print(f"   Lines: {covered_lines}/{total_lines}")
    print(f"   Branches: {covered_branches}/{num_branches}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_coverage.py <coverage.json> <output.json>")
        sys.exit(1)
    
    extract_coverage(sys.argv[1], sys.argv[2])
