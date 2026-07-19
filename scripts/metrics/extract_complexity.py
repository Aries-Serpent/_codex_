#!/usr/bin/env python3
"""
Extract code complexity metrics from radon output.

Analyzes cyclomatic and cognitive complexity:
- Average complexity per function
- High-complexity outliers
- Maintainability index
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def extract_complexity(
    cyclomatic_json: str,
    maintainability_json: str,
    output_path: str
) -> None:
    """Extract code complexity metrics."""
    
    # Load cyclomatic complexity
    try:
        with open(cyclomatic_json) as f:
            cyclomatic_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cyclomatic_data = {}
    
    # Load maintainability index
    try:
        with open(maintainability_json) as f:
            maintainability_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        maintainability_data = {}
    
    # Calculate aggregate complexity
    complexities = []
    high_complexity_functions = []
    
    for file_path, file_data in cyclomatic_data.items():
        if isinstance(file_data, dict):
            for func_name, metrics in file_data.items():
                if isinstance(metrics, dict):
                    cc = metrics.get('complexity', 0)
                    complexities.append(cc)
                    
                    if cc > 15:  # High complexity threshold
                        high_complexity_functions.append({
                            'file': file_path,
                            'function': func_name,
                            'cyclomatic_complexity': cc,
                        })
    
    # Calculate statistics
    avg_complexity = sum(complexities) / len(complexities) if complexities else 0
    max_complexity = max(complexities) if complexities else 0
    
    # Get average maintainability index
    maintainability_indices = []
    if maintainability_data:
        for file_path, index_data in maintainability_data.items():
            if isinstance(index_data, dict):
                mi = index_data.get('mi', 0)
                maintainability_indices.append(mi)
    
    avg_mi = sum(maintainability_indices) / len(maintainability_indices) if maintainability_indices else 0
    
    # Sort high complexity by complexity descending
    high_complexity_functions.sort(key=lambda x: x['cyclomatic_complexity'], reverse=True)
    
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "code_complexity",
        "cyclomatic_complexity": {
            "average": round(avg_complexity, 2),
            "maximum": max_complexity,
            "threshold": 15,
            "exceeding_threshold": len(high_complexity_functions),
        },
        "maintainability_index": {
            "average": round(avg_mi, 2),
            "target": 70,  # Higher is better (0-100 scale)
        },
        "high_complexity_functions": high_complexity_functions[:20],  # Top 20
        "source": "radon",
        "targets": {
            "cyclomatic_complexity_avg": 10.0,
            "maintainability_index_avg": 70.0,
        },
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Complexity metrics written to {output_path}")
    print(f"   Avg cyclomatic: {avg_complexity:.2f}")
    print(f"   High complexity functions: {len(high_complexity_functions)}")
    print(f"   Avg maintainability index: {avg_mi:.2f}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: extract_complexity.py <cyclomatic.json> <maintainability.json> <output.json>")
        sys.exit(1)
    
    extract_complexity(sys.argv[1], sys.argv[2], sys.argv[3])
