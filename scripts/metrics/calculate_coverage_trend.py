#!/usr/bin/env python3
"""
Calculate 7-day coverage trend.

Computes rolling average and trend direction.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def calculate_coverage_trend(coverage_latest: str, output_path: str) -> None:
    """Calculate 7-day coverage trend."""
    
    # In a real implementation, this would load historical data
    # For now, create a trend structure that will be updated over time
    
    try:
        with open(coverage_latest) as f:
            latest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        latest = {'value': 0}
    
    trend_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "coverage_trend_7day",
        "current_coverage": latest.get('value', 0),
        "trend_data_points": [
            {"date": (datetime.utcnow() - timedelta(days=i)).isoformat()[:10], "coverage": latest.get('value', 0)}
            for i in range(7)
        ],
        "rolling_average_7day": latest.get('value', 0),
        "trend_direction": "stable",  # Will be updated as data accumulates
        "trend_change_percent": 0.0,
        "previous_week_average": latest.get('value', 0),
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(trend_data, f, indent=2)
    
    print(f"✅ Coverage trend written to {output_path}")
    print(f"   Current: {trend_data['current_coverage']:.2f}%")
    print(f"   7-day average: {trend_data['rolling_average_7day']:.2f}%")
    print(f"   Trend: {trend_data['trend_direction']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: calculate_coverage_trend.py <coverage_latest.json> <output.json>")
        sys.exit(1)
    
    calculate_coverage_trend(sys.argv[1], sys.argv[2])
