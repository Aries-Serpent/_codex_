#!/usr/bin/env python3
"""
Generate metrics index and dashboard JSON.

Aggregates all metrics into a single index file and dashboard view.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def generate_metrics_index(metrics_dir: str, output_path: str) -> None:
    """Generate index of all metrics files."""
    
    metrics_path = Path(metrics_dir)
    if not metrics_path.exists():
        print(f"Metrics directory not found: {metrics_dir}")
        sys.exit(1)
    
    # Find all JSON metric files
    metric_files = list(metrics_path.glob("*.json"))
    
    index = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metrics_directory": metrics_dir,
        "total_metrics": len(metric_files),
        "metrics": [],
    }
    
    # Load each metric file
    for metric_file in sorted(metric_files):
        try:
            with open(metric_file) as f:
                metric_data = json.load(f)
            
            metric_entry = {
                "filename": metric_file.name,
                "metric_id": metric_data.get('metric_id', 'unknown'),
                "timestamp": metric_data.get('timestamp', 'unknown'),
            }
            
            # Extract key values
            if metric_data.get('metric_id') == 'coverage_overall':
                metric_entry['value'] = metric_data.get('value')
                metric_entry['unit'] = metric_data.get('unit')
                metric_entry['target'] = metric_data.get('target')
                metric_entry['status'] = metric_data.get('status')
            
            index['metrics'].append(metric_entry)
        
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON in {metric_file.name}")
            continue
    
    # Write index
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ Metrics index written to {output_path}")
    print(f"   Total metrics files: {len(metric_files)}")


def generate_dashboard(metrics_dir: str, output_path: str) -> None:
    """Generate dashboard JSON from all metrics."""
    
    metrics_path = Path(metrics_dir)
    
    dashboard = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "status": "operational",
        "sections": {},
    }
    
    # Load key metrics for dashboard
    key_files = {
        'coverage': 'coverage_latest.json',
        'test_metrics': 'test_count_latest.json',
        'test_latency': 'test_latency_latest.json',
        'complexity': 'code_complexity_latest.json',
        'security': 'security_vulnerabilities_latest.json',
        'slo_compliance': 'slo_compliance_latest.json',
    }
    
    for section_name, filename in key_files.items():
        file_path = metrics_path / filename
        try:
            with open(file_path) as f:
                dashboard['sections'][section_name] = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Missing dashboard section: {filename}")
            continue
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON in dashboard section: {filename}")
            continue
    
    # Write dashboard
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"✅ Dashboard generated at {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_metrics_index.py <metrics_dir> <index_output.json>")
        print("       generate_dashboard.py <metrics_dir> <dashboard_output.json>")
        sys.exit(1)
    
    script_name = Path(sys.argv[0]).name
    if 'index' in script_name:
        generate_metrics_index(sys.argv[1], sys.argv[2])
    else:
        generate_dashboard(sys.argv[1], sys.argv[2])
