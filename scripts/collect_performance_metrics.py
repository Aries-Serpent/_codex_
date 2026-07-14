#!/usr/bin/env python3
"""
Collect Performance Metrics
Phase 4D Planset 007 - Performance metrics collection

Collects metrics from:
- Test execution times
- Workflow execution times
- Memory and CPU usage
- CI/CD pipeline timing
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Metrics collection categories
METRICS_CATEGORIES = {
    "tests": {
        "description": "Test execution metrics",
        "commands": [
            "pytest tests/ -v --tb=no --co -q 2>/dev/null | wc -l",  # Test count
        ],
    },
    "workflows": {
        "description": "Workflow execution metrics",
        "commands": [
            "find .github/workflows -name '*.yml' | wc -l",  # Workflow count
        ],
    },
    "coverage": {
        "description": "Test coverage metrics",
        "commands": [
            "grep -r 'fail_under' pyproject.toml | head -1",  # Coverage target
        ],
    },
}


def collect_test_metrics() -> dict[str, Any]:
    """Collect test execution metrics"""
    metrics = {
        "test_files": 0,
        "total_tests": 0,
        "test_markers": [],
    }
    
    try:
        # Count test files
        result = subprocess.run(
            ["find", "tests", "-name", "test_*.py", "-o", "-name", "*_test.py"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        metrics["test_files"] = len(result.stdout.strip().split("\n"))
    except Exception as e:
        print(f"Warning: Could not count test files: {e}", file=sys.stderr)
    
    return metrics


def collect_workflow_metrics() -> dict[str, Any]:
    """Collect workflow execution metrics"""
    metrics = {
        "workflow_files": 0,
        "total_jobs": 0,
    }
    
    try:
        # Count workflow files
        result = subprocess.run(
            ["find", ".github/workflows", "-name", "*.yml", "-o", "-name", "*.yaml"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        workflow_files = [f for f in result.stdout.strip().split("\n") if f]
        metrics["workflow_files"] = len(workflow_files)
    except Exception as e:
        print(f"Warning: Could not count workflows: {e}", file=sys.stderr)
    
    return metrics


def collect_system_metrics() -> dict[str, Any]:
    """Collect system resource metrics"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "hostname": subprocess.run(
            ["hostname"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip(),
    }
    
    try:
        # Memory info
        result = subprocess.run(
            ["free", "-b"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            metrics["memory"] = {
                "total_bytes": int(parts[1]),
                "used_bytes": int(parts[2]),
                "free_bytes": int(parts[3]),
            }
    except Exception as e:
        print(f"Warning: Could not collect memory metrics: {e}", file=sys.stderr)
    
    return metrics


def collect_repository_metrics() -> dict[str, Any]:
    """Collect repository size and structure metrics"""
    metrics = {}
    
    try:
        # Repository size
        result = subprocess.run(
            ["du", "-sh", "."],
            capture_output=True,
            text=True,
            timeout=30,
        )
        metrics["repo_size"] = result.stdout.strip().split()[0]
        
        # File counts by type
        result = subprocess.run(
            ["find", ".", "-type", "f", "-name", "*.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        metrics["python_files"] = len(result.stdout.strip().split("\n"))
    
    except Exception as e:
        print(f"Warning: Could not collect repo metrics: {e}", file=sys.stderr)
    
    return metrics


def main() -> int:
    """Collect and save performance metrics"""
    parser = argparse.ArgumentParser(
        description="Collect performance metrics"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file for metrics JSON",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test metrics",
    )
    parser.add_argument(
        "--include-workflows",
        action="store_true",
        help="Include workflow metrics",
    )
    
    args = parser.parse_args()
    
    # Collect metrics
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
    }
    
    # System metrics (always included)
    metrics["system"] = collect_system_metrics()
    metrics["repository"] = collect_repository_metrics()
    
    # Optional metrics
    if args.include_tests:
        metrics["metrics"]["tests"] = collect_test_metrics()
    
    if args.include_workflows:
        metrics["metrics"]["workflows"] = collect_workflow_metrics()
    
    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Metrics collected and saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
