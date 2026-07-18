#!/usr/bin/env python3
"""
Check SLO compliance against module coverage.

Compares actual module coverage against defined SLO targets.
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


def check_slo_compliance(
    slos_yaml: str,
    module_coverage_json: str,
    output_path: str
) -> None:
    """Check module coverage against SLOs."""
    
    # Load SLOs
    slos = {}
    if yaml:
        try:
            with open(slos_yaml) as f:
                slo_config = yaml.safe_load(f)
                modules = slo_config.get('modules', {})
                for module_name, module_config in modules.items():
                    slos[module_name] = {
                        'target': module_config.get('target', 50),
                        'category': module_config.get('category', 'utility'),
                    }
        except FileNotFoundError:
            print(f"SLO file not found: {slos_yaml}")
    
    # Load module coverage
    try:
        with open(module_coverage_json) as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        print(f"Module coverage file not found: {module_coverage_json}")
        coverage_data = {'modules': {}}
    except json.JSONDecodeError:
        coverage_data = {'modules': {}}
    
    modules = coverage_data.get('modules', {})
    
    # Check compliance
    compliance = {
        'total_modules': len(slos),
        'compliant_modules': 0,
        'non_compliant_modules': [],
        'by_category': {
            'critical': {'compliant': 0, 'total': 0},
            'core': {'compliant': 0, 'total': 0},
            'utility': {'compliant': 0, 'total': 0},
        },
    }
    
    for module_name, slo_info in slos.items():
        category = slo_info['category']
        target = slo_info['target']
        
        compliance['by_category'][category]['total'] += 1
        
        # Find matching module in coverage data
        actual_coverage = None
        for coverage_module, coverage_info in modules.items():
            # Try to match module paths
            if module_name.replace('_', '/').lower() in coverage_module.lower() or \
               coverage_module.lower() in module_name.replace('_', '/').lower():
                actual_coverage = coverage_info.get('coverage', 0)
                break
        
        if actual_coverage is not None:
            if actual_coverage >= target:
                compliance['compliant_modules'] += 1
                compliance['by_category'][category]['compliant'] += 1
            else:
                compliance['non_compliant_modules'].append({
                    'module': module_name,
                    'category': category,
                    'target': target,
                    'actual': actual_coverage,
                    'gap': target - actual_coverage,
                })
    
    # Sort non-compliant by gap (largest first)
    compliance['non_compliant_modules'].sort(key=lambda x: x['gap'], reverse=True)
    
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "slo_compliance",
        "compliance": compliance,
        "compliance_percentage": (
            compliance['compliant_modules'] / compliance['total_modules'] * 100
            if compliance['total_modules'] > 0 else 0
        ),
        "source": "slo-checker",
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ SLO compliance written to {output_path}")
    print(f"   Compliance: {output['compliance_percentage']:.1f}%")
    print(f"   Compliant: {compliance['compliant_modules']}/{compliance['total_modules']}")
    print(f"   Non-compliant: {len(compliance['non_compliant_modules'])}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: check_slo_compliance.py <slos.yaml> <module_coverage.json> <output.json>")
        sys.exit(1)
    
    check_slo_compliance(sys.argv[1], sys.argv[2], sys.argv[3])
