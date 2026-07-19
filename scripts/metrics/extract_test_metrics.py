#!/usr/bin/env python3
"""
Extract test count and distribution metrics.

Analyzes pytest collection to count tests by category:
- Unit tests
- Integration tests
- E2E tests
- Performance tests
- Slow tests (>30s)
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def extract_test_metrics(collection_json_path: str, output_path: str) -> None:
    """Extract test count and distribution metrics."""
    
    try:
        with open(collection_json_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Test collection file not found: {collection_json_path}")
        # Create default output if file not found
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metric_id": "test_count",
            "total_tests": 0,
            "by_category": {},
            "status": "no_data",
        }
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON in test collection file: {collection_json_path}")
        return
    
    # Count tests
    tests = data.get('tests', [])
    
    # Categorize tests
    categories = {
        'unit': 0,
        'integration': 0,
        'e2e': 0,
        'performance': 0,
        'smoke': 0,
        'other': 0,
    }
    
    markers_found = {}
    
    for test in tests:
        # Check test path for category hints
        test_path = test.get('nodeid', '')
        markers = test.get('markers', []) if isinstance(test.get('markers'), list) else []
        
        # Store all markers
        for marker in markers:
            marker_name = marker if isinstance(marker, str) else marker.get('name', 'unknown')
            markers_found[marker_name] = markers_found.get(marker_name, 0) + 1
        
        # Categorize based on markers or path
        if 'unit' in markers or 'test_unit' in test_path.lower():
            categories['unit'] += 1
        elif 'integration' in markers or 'test_integration' in test_path.lower():
            categories['integration'] += 1
        elif 'e2e' in markers or 'test_e2e' in test_path.lower():
            categories['e2e'] += 1
        elif 'perf' in markers or 'performance' in markers:
            categories['performance'] += 1
        elif 'smoke' in markers:
            categories['smoke'] += 1
        else:
            categories['other'] += 1
    
    total_tests = len(tests)
    
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "test_count",
        "total_tests": total_tests,
        "by_category": categories,
        "by_marker": markers_found,
        "status": "collected" if total_tests > 0 else "no_tests",
        "source": "pytest-collect-only",
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Test metrics written to {output_path}")
    print(f"   Total tests: {total_tests}")
    for category, count in categories.items():
        if count > 0:
            pct = (count / total_tests) * 100 if total_tests > 0 else 0
            print(f"   {category}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_test_metrics.py <test_collection.json> <output.json>")
        sys.exit(1)
    
    extract_test_metrics(sys.argv[1], sys.argv[2])
