#!/usr/bin/env python3
"""
Safe input validation script for GitHub Actions workflows.

This script provides safe validation for workflow inputs without using
shell metacaharacters or regex that could be exploited.

Usage:
  python3 .github/scripts/validate_workflow_inputs.py --type manifest-path --value "${{ github.event.inputs.manifest_path }}"
  python3 .github/scripts/validate_workflow_inputs.py --type discussion-numbers --value "${{ github.event.inputs.discussion_numbers }}"
"""

import argparse
import json
import os
import sys
from pathlib import Path


def validate_manifest_path(value):
    """
    Validate that the manifest path is safe and exists.
    
    SAFE PATTERNS:
    - Uses pathlib.Path for safe path handling (no shell metacharacters)
    - Checks path safety without shell syntax
    - Returns JSON output for workflow consumption
    
    Args:
        value: Manifest file path from workflow input
        
    Returns:
        dict with 'valid' (bool), 'path' (str), and optionally 'error'
    """
    if not value or not value.strip():
        return {
            'valid': False,
            'mode': 'direct',
            'reason': 'manifest_path is empty, using direct mode'
        }

    try:
        # Convert to Path object - this prevents shell injection
        manifest_path = Path(value.strip())

        # Security checks:
        # 1. No absolute paths outside repo
        # 2. No parent directory traversal (..)
        # 3. Must be within repo bounds

        # Resolve to absolute path to detect traversal
        abs_path = manifest_path.resolve()
        repo_root = Path.cwd().resolve()

        # Check if path tries to escape repo
        if not str(abs_path).startswith(str(repo_root)):
            return {
                'valid': False,
                'mode': 'direct',
                'reason': f'manifest_path escapes repo bounds: {abs_path}',
                'error_type': 'path_traversal'
            }

        # Check if file exists
        if not abs_path.is_file():
            return {
                'valid': False,
                'mode': 'direct',
                'reason': f'manifest_path does not exist: {abs_path}',
                'error_type': 'file_not_found'
            }

        # Check if it's actually a manifest file (basic validation)
        if abs_path.suffix not in ['.json', '.yml', '.yaml']:
            return {
                'valid': False,
                'mode': 'direct',
                'reason': f'manifest_path has invalid extension: {abs_path.suffix}',
                'error_type': 'invalid_extension'
            }

        return {
            'valid': True,
            'mode': 'manifest',
            'path': str(abs_path.relative_to(repo_root)),
            'reason': 'manifest_path validated successfully'
        }

    except Exception as e:
        return {
            'valid': False,
            'mode': 'direct',
            'reason': f'Error validating manifest_path: {str(e)}',
            'error_type': 'validation_error'
        }


def validate_discussion_numbers(value):
    """
    Validate discussion numbers input.
    
    SAFE PATTERNS:
    - Uses int() for type validation (no regex)
    - Validates each number individually
    - Returns parsed integers in JSON
    
    Args:
        value: Whitespace or comma-separated discussion numbers
        
    Returns:
        dict with 'valid' (bool), 'numbers' (list), and optionally 'error'
    """
    if not value or not value.strip():
        # Use defaults
        return {
            'valid': True,
            'numbers': [3756, 3673],
            'reason': 'discussion_numbers empty, using defaults',
            'using_defaults': True
        }

    try:
        # Split by whitespace and commas
        raw_numbers = value.replace(',', ' ').split()

        # Try to parse each as integer (safe - will raise ValueError if not)
        numbers = []
        for num_str in raw_numbers:
            if num_str.strip():
                num = int(num_str.strip())
                # Validate reasonable range (GH discussion IDs are typically positive)
                if num <= 0:
                    return {
                        'valid': False,
                        'reason': f'discussion number must be positive: {num}',
                        'error_type': 'invalid_value'
                    }
                numbers.append(num)

        if not numbers:
            return {
                'valid': False,
                'reason': 'no valid discussion numbers found',
                'error_type': 'empty_list'
            }

        return {
            'valid': True,
            'numbers': numbers,
            'reason': f'Parsed {len(numbers)} discussion number(s)',
            'using_defaults': False
        }

    except ValueError as e:
        return {
            'valid': False,
            'reason': f'Invalid discussion number format: {str(e)}',
            'error_type': 'parse_error'
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Safe workflow input validation'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=['manifest-path', 'discussion-numbers'],
        help='Type of input to validate'
    )
    parser.add_argument(
        '--value',
        required=True,
        help='Input value to validate'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        default=True,
        help='Output JSON (default)'
    )

    args = parser.parse_args()

    # Validate based on type
    if args.type == 'manifest-path':
        result = validate_manifest_path(args.value)
    elif args.type == 'discussion-numbers':
        result = validate_discussion_numbers(args.value)
    else:
        result = {'valid': False, 'reason': 'Unknown validation type'}

    # Output JSON
    print(json.dumps(result))

    # Exit with appropriate code
    sys.exit(0 if result.get('valid', False) else 1)


if __name__ == '__main__':
    main()
