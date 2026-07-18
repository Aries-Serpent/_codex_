#!/usr/bin/env python3
"""
Extract test latency metrics from pytest output.

Parses pytest --durations output to calculate:
- p50, p95, p99 latency percentiles
- Slow tests (>30s)
- Average test duration
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


def extract_latency(latency_log_path: str, output_path: str) -> None:
    """Extract test latency metrics from pytest output."""
    
    durations: List[float] = []
    slow_tests: List[Tuple[str, float]] = []
    
    try:
        with open(latency_log_path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Latency log not found: {latency_log_path}")
        # Create default output
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metric_id": "test_latency",
            "p50": 0,
            "p95": 0,
            "p99": 0,
            "average": 0,
            "slow_tests": [],
            "status": "no_data",
        }
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        return
    
    # Parse pytest durations lines
    # Format: "0.12s call     test_module::test_function"
    duration_pattern = r'(\d+\.?\d*)\s*s\s+(\w+)\s+(.*)'
    
    for line in lines:
        match = re.search(duration_pattern, line)
        if match:
            duration = float(match.group(1))
            phase = match.group(2)  # setup, call, teardown
            test_name = match.group(3)
            
            # Only count actual test execution
            if phase == 'call':
                durations.append(duration)
                
                if duration > 30.0:
                    slow_tests.append((test_name.strip(), duration))
    
    # Sort for percentile calculation
    durations.sort()
    
    if durations:
        n = len(durations)
        p50_idx = int(n * 0.50)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)
        
        p50 = durations[p50_idx] if p50_idx < n else durations[-1]
        p95 = durations[p95_idx] if p95_idx < n else durations[-1]
        p99 = durations[p99_idx] if p99_idx < n else durations[-1]
        average = sum(durations) / n
    else:
        p50 = p95 = p99 = average = 0.0
    
    # Sort slow tests
    slow_tests.sort(key=lambda x: x[1], reverse=True)
    
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "test_latency",
        "p50": round(p50, 2),
        "p95": round(p95, 2),
        "p99": round(p99, 2),
        "average": round(average, 2),
        "total_tests": len(durations),
        "slow_tests_count": len(slow_tests),
        "slow_tests_examples": [
            {"test": name, "duration_seconds": duration}
            for name, duration in slow_tests[:10]  # Top 10 slowest
        ],
        "targets": {
            "p50": 2.0,
            "p95": 10.0,
            "p99": 30.0,
        },
        "source": "pytest-durations",
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Test latency metrics written to {output_path}")
    print(f"   Tests analyzed: {len(durations)}")
    print(f"   p50: {p50:.2f}s (target: 2.0s)")
    print(f"   p95: {p95:.2f}s (target: 10.0s)")
    print(f"   p99: {p99:.2f}s (target: 30.0s)")
    print(f"   Slow tests (>30s): {len(slow_tests)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_latency.py <latency.log> <output.json>")
        sys.exit(1)
    
    extract_latency(sys.argv[1], sys.argv[2])
