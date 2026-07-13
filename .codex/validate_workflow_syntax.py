#!/usr/bin/env python3
"""
Validate all GitHub Actions workflows for YAML syntax errors.

This script ensures all workflow files in .github/workflows/ are valid YAML
and follow GitHub Actions workflow schema.

Usage:
    python validate_workflow_syntax.py [--verbose] [--json]
    
Options:
    --verbose  Show detailed information for each workflow
    --json     Output results in JSON format
"""

import subprocess
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def get_workflow_files() -> List[Path]:
    """Get all workflow files from .github/workflows directory."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        return []
    
    return sorted(workflows_dir.glob("*.yml"))


def validate_yaml_syntax(file_path: Path) -> Tuple[bool, str]:
    """
    Validate YAML syntax for a workflow file.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_workflow_structure(file_path: Path, data: dict) -> Tuple[bool, List[str]]:
    """
    Validate workflow structure and required fields.
    
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Check for required top-level keys
    if "name" not in data:
        warnings.append("Missing 'name' field")
    
    if "on" not in data:
        warnings.append("Missing 'on' (trigger) section")
    
    if "jobs" not in data:
        warnings.append("Missing 'jobs' section")
    
    # Check for recommended keys
    if "permissions" not in data:
        warnings.append("Missing 'permissions' section (security best practice)")
    
    # Check that jobs are properly structured
    jobs = data.get("jobs", {})
    if isinstance(jobs, dict):
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                warnings.append(f"Job '{job_name}' is not properly configured")
                continue
            
            if "runs-on" not in job_config and "uses" not in job_config:
                warnings.append(f"Job '{job_name}' missing 'runs-on' or 'uses'")
    
    return len(warnings) == 0, warnings


def validate_workflows(verbose: bool = False, json_output: bool = False) -> int:
    """
    Validate all workflows.
    
    Returns:
        Exit code (0 for success, 1 for errors)
    """
    workflows = get_workflow_files()
    
    if not workflows:
        if verbose:
            print("No workflows found in .github/workflows/")
        return 0
    
    results = {
        "total": len(workflows),
        "valid": 0,
        "invalid": 0,
        "warnings": 0,
        "workflows": []
    }
    
    for workflow_file in workflows:
        # Validate YAML syntax
        is_valid, error = validate_yaml_syntax(workflow_file)
        
        result = {
            "file": workflow_file.name,
            "syntax_valid": is_valid,
            "errors": [],
            "warnings": []
        }
        
        if not is_valid:
            result["errors"].append(error)
            results["invalid"] += 1
        else:
            results["valid"] += 1
            
            # Load and validate structure
            try:
                with open(workflow_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                _, warnings = validate_workflow_structure(workflow_file, data or {})
                if warnings:
                    result["warnings"] = warnings
                    results["warnings"] += len(warnings)
            except Exception as e:
                result["errors"].append(f"Structure validation failed: {e}")
        
        results["workflows"].append(result)
    
    # Output results
    if json_output:
        print(json.dumps(results, indent=2))
    else:
        print(f"Workflow Validation Report")
        print(f"{'=' * 60}")
        print(f"Total workflows: {results['total']}")
        print(f"✓ Valid: {results['valid']}")
        print(f"✗ Invalid: {results['invalid']}")
        print(f"⚠ Warnings: {results['warnings']}")
        print()
        
        # Show invalid workflows
        invalid_workflows = [w for w in results['workflows'] if not w['syntax_valid']]
        if invalid_workflows:
            print("Invalid Workflows:")
            for w in invalid_workflows:
                print(f"  ✗ {w['file']}")
                for error in w['errors']:
                    print(f"    └─ {error[:80]}")
            print()
        
        # Show warnings if verbose
        if verbose:
            warned_workflows = [w for w in results['workflows'] if w['warnings']]
            if warned_workflows:
                print("Workflows with Warnings:")
                for w in warned_workflows:
                    print(f"  ⚠ {w['file']}")
                    for warning in w['warnings']:
                        print(f"    └─ {warning}")
                print()
        
        # Summary line
        if results['invalid'] == 0:
            print(f"✅ All {results['total']} workflows pass syntax validation")
            return 0
        else:
            print(f"❌ {results['invalid']} workflow(s) have syntax errors")
            return 1


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    json_output = "--json" in sys.argv
    
    exit_code = validate_workflows(verbose=verbose, json_output=json_output)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
