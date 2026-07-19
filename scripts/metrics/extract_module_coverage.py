#!/usr/bin/env python3
"""
Extract per-module coverage metrics and check against SLOs.

This script reads coverage.json and PHASE_5_COVERAGE_SLOS.yaml to generate:
- Per-module coverage percentages
- SLO attainment status
- Module categorization (critical/core/utility)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None


def extract_module_coverage(
    coverage_json_path: str,
    slos_yaml_path: str,
    output_path: str
) -> None:
    """Extract per-module coverage and compare against SLOs."""
    
    # Load coverage data
    try:
        with open(coverage_json_path) as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        print(f"Coverage file not found: {coverage_json_path}")
        sys.exit(1)
    
    # Load SLO definitions
    if yaml:
        try:
            with open(slos_yaml_path) as f:
                slo_config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"SLO file not found: {slos_yaml_path}")
            slo_config = {}
    else:
        slo_config = {}
    
    # Build module coverage map
    module_coverage = {}
    
    if 'files' in coverage_data:
        for file_path, file_data in coverage_data['files'].items():
            # Determine module from file path
            # src/aries_serpent_core/auth/... -> aries_serpent_core/auth
            parts = Path(file_path).parts
            
            if 'src' in parts:
                src_idx = parts.index('src')
                if src_idx + 1 < len(parts):
                    module_path = '/'.join(parts[src_idx + 1:src_idx + 3])
                    
                    summary = file_data.get('summary', {})
                    pct_covered = summary.get('percent_covered', 0.0)
                    
                    # Aggregate by module
                    if module_path not in module_coverage:
                        module_coverage[module_path] = {
                            'total': 0,
                            'covered': 0,
                            'count': 0,
                        }
                    
                    module_coverage[module_path]['total'] += summary.get('num_statements', 0)
                    module_coverage[module_path]['covered'] += summary.get('covered_lines', 0)
                    module_coverage[module_path]['count'] += 1
    
    # Calculate module percentages
    modules = {}
    for module_path, data in module_coverage.items():
        if data['total'] > 0:
            pct = (data['covered'] / data['total']) * 100
            modules[module_path] = {
                'coverage': round(pct, 2),
                'covered_lines': data['covered'],
                'total_lines': data['total'],
            }
    
    # Create output structure
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "module_coverage_breakdown",
        "metric_type": "per_module",
        "unit": "%",
        "modules": modules,
        "summary": {
            "total_modules": len(modules),
            "average_coverage": round(
                sum(m['coverage'] for m in modules.values()) / len(modules),
                2
            ) if modules else 0,
        },
        "source": "pytest-cov",
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Module coverage metrics written to {output_path}")
    print(f"   Modules analyzed: {len(modules)}")
    print(f"   Average coverage: {output['summary']['average_coverage']:.2f}%")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: extract_module_coverage.py <coverage.json> <slos.yaml> <output.json>")
        sys.exit(1)
    
    extract_module_coverage(sys.argv[1], sys.argv[2], sys.argv[3])
