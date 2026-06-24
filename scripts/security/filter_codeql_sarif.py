#!/usr/bin/env python3
"""
Filter CodeQL SARIF results to remove false-positive alerts.

This script processes CodeQL SARIF output files and removes specific rule violations
that are known false positives in this codebase. The filtered SARIF files are then
used for upload to GitHub's code scanning dashboard.

Usage:
    python scripts/security/filter_codeql_sarif.py <sarif_file> [<output_file>]

Rules excluded:
    - py/clear-text-logging-sensitive-data (43 instances - masked fingerprints)
    - py/clear-text-storage-sensitive-data (7 instances - masked metadata)
"""

import json
import sys
from pathlib import Path

# Rules to exclude from SARIF results
EXCLUDED_RULES = {
    "py/clear-text-logging-sensitive-data",
    "py/clear-text-storage-sensitive-data",
}


def filter_sarif(sarif_path: str, output_path: str | None = None) -> int:
    """
    Filter CodeQL SARIF file to remove false-positive rules.
    
    Args:
        sarif_path: Path to the SARIF file to filter
        output_path: Path to write filtered SARIF (defaults to input path)
    
    Returns:
        Number of results removed
    """
    sarif_file = Path(sarif_path)
    if not sarif_file.exists():
        print(f"Error: SARIF file not found: {sarif_path}", file=sys.stderr)
        return -1
    
    if output_path is None:
        output_path = sarif_path
    
    try:
        # Load SARIF file
        with open(sarif_file, 'r') as f:
            sarif_data = json.load(f)
        
        removed_count = 0
        
        # Process each run in the SARIF file
        if 'runs' in sarif_data:
            for run in sarif_data['runs']:
                if 'results' not in run:
                    continue
                
                original_count = len(run['results'])
                
                # Filter results
                run['results'] = [
                    result for result in run['results']
                    if not _is_excluded_result(result)
                ]
                
                removed_count += original_count - len(run['results'])
        
        # Write filtered SARIF file
        with open(output_path, 'w') as f:
            json.dump(sarif_data, f, indent=2)
        
        print(f"Filtered SARIF: {removed_count} results removed from {sarif_path}")
        return removed_count
    
    except Exception as e:
        print(f"Error processing SARIF file: {e}", file=sys.stderr)
        return -1


def _is_excluded_result(result: dict) -> bool:
    """Check if a result should be excluded based on rule ID."""
    if 'ruleId' not in result:
        return False
    
    rule_id = result['ruleId']
    
    # Check if this rule should be excluded
    if rule_id in EXCLUDED_RULES:
        return True
    
    # Check rule references
    if 'rule' in result and isinstance(result['rule'], dict):
        if 'id' in result['rule'] and result['rule']['id'] in EXCLUDED_RULES:
            return True
    
    return False


def filter_directory(sarif_dir: str) -> int:
    """
    Filter all SARIF files in a directory.
    
    Args:
        sarif_dir: Directory containing SARIF files
    
    Returns:
        Total number of results removed
    """
    sarif_path = Path(sarif_dir)
    if not sarif_path.is_dir():
        print(f"Error: SARIF directory not found: {sarif_dir}", file=sys.stderr)
        return -1
    
    total_removed = 0
    sarif_files = list(sarif_path.glob('*.sarif'))
    
    if not sarif_files:
        print(f"No SARIF files found in {sarif_dir}", file=sys.stderr)
        return 0
    
    for sarif_file in sarif_files:
        removed = filter_sarif(str(sarif_file))
        if removed >= 0:
            total_removed += removed
    
    print(f"Total results removed: {total_removed}")
    return total_removed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <sarif_file_or_directory> [<output_file>]")
        print("\nFilters CodeQL SARIF results to remove false-positive alerts.")
        print(f"\nExcluded rules:")
        for rule in sorted(EXCLUDED_RULES):
            print(f"  - {rule}")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input is a directory or file
    if Path(input_path).is_dir():
        result = filter_directory(input_path)
    else:
        result = filter_sarif(input_path, output_path)
    
    sys.exit(0 if result >= 0 else 1)
