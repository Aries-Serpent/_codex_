#!/usr/bin/env python3
"""
Security Findings API

Purpose:
    Query-based API for accessing security findings from cache or comprehensive JSON.
    Supports filtering by CWE, package, file path, and severity with multiple output formats.

Usage:
    python scripts/ci/security_findings_api.py query \
      --query-type cwe \
      --value CWE-79 \
      --cache-dir .codex/security-cache \
      --output findings.json

    python scripts/ci/security_findings_api.py query \
      --query-type severity \
      --value CRITICAL \
      --format markdown

Environment Variables:
    SECURITY_FINDINGS_CACHE: Override default cache directory
    SECURITY_FINDINGS_JSON: Override comprehensive findings file path

Exit Codes:
    0: Success
    1: Error (validation, file I/O, etc.)
    2: No findings found
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_CACHE_DIR = Path(".codex/security-cache")
DEFAULT_FINDINGS_FILE = Path(".codex/security-findings-comprehensive.json")
VALID_QUERY_TYPES = {'cwe', 'package', 'file', 'severity'}
VALID_FORMATS = {'json', 'csv', 'markdown'}
SEVERITY_LEVELS = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}


def validate_query_type(query_type: str) -> bool:
    """Validate query type is supported."""
    return query_type.lower() in VALID_QUERY_TYPES


def validate_severity(severity: str) -> bool:
    """Validate severity level is recognized."""
    return severity.upper() in SEVERITY_LEVELS


def load_findings(cache_dir: Optional[Path] = None, 
                  findings_file: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load findings from cache or comprehensive file.
    
    Args:
        cache_dir: Path to security cache directory
        findings_file: Path to comprehensive findings JSON
        
    Returns:
        List of finding dictionaries
        
    Raises:
        FileNotFoundError: If no findings source exists
    """
    cache_dir = cache_dir or DEFAULT_CACHE_DIR
    findings_file = findings_file or DEFAULT_FINDINGS_FILE
    
    # Try cache first (latest run)
    if cache_dir.exists():
        index_file = cache_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index = json.load(f)
                    if index.get('runs') and len(index['runs']) > 0:
                        latest_run = index['runs'][-1]  # Most recent run
                        run_file = cache_dir / "runs" / f"{latest_run['run_id']}.json"
                        if run_file.exists():
                            with open(run_file, 'r') as rf:
                                data = json.load(rf)
                                logger.info(f"Loaded findings from cache: {run_file}")
                                return data.get('findings', [])
            except (json.JSONDecodeError, KeyError, OSError) as e:
                logger.warning(f"Cache read failed: {e}, falling back to comprehensive file")
    
    # Fallback to comprehensive findings file
    if findings_file.exists():
        try:
            with open(findings_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded findings from: {findings_file}")
                return data.get('findings', [])
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load findings file: {e}")
            raise FileNotFoundError(f"Cannot load findings: {findings_file}")
    
    raise FileNotFoundError(f"No findings source found in {cache_dir} or {findings_file}")


def filter_by_cwe(findings: List[Dict[str, Any]], cwe_id: str) -> List[Dict[str, Any]]:
    """
    Filter findings by CWE ID (e.g., CWE-79).
    
    Args:
        findings: List of finding dictionaries
        cwe_id: CWE identifier (case-insensitive, with or without CWE- prefix)
        
    Returns:
        Filtered list of findings
    """
    # Normalize CWE ID
    cwe_normalized = cwe_id.upper()
    if not cwe_normalized.startswith('CWE-'):
        cwe_normalized = f'CWE-{cwe_normalized}'
    
    matching = []
    for finding in findings:
        if finding.get('cwe_id'):
            if finding['cwe_id'].upper() == cwe_normalized:
                matching.append(finding)
    
    return matching


def filter_by_package(findings: List[Dict[str, Any]], package_name: str) -> List[Dict[str, Any]]:
    """
    Filter findings by package name (case-insensitive).
    
    Args:
        findings: List of finding dictionaries
        package_name: Package name to filter by
        
    Returns:
        Filtered list of findings
    """
    package_lower = package_name.lower()
    matching = []
    
    for finding in findings:
        if finding.get('package'):
            if finding['package'].lower() == package_lower:
                matching.append(finding)
    
    return matching


def filter_by_file(findings: List[Dict[str, Any]], file_path: str) -> List[Dict[str, Any]]:
    """
    Filter findings by file path (exact or prefix match).
    
    Args:
        findings: List of finding dictionaries
        file_path: File path to filter by (can be partial)
        
    Returns:
        Filtered list of findings
    """
    file_normalized = file_path.replace('\\', '/')
    matching = []
    
    for finding in findings:
        if finding.get('file'):
            file_in_finding = finding['file'].replace('\\', '/')
            if file_in_finding == file_normalized or file_in_finding.endswith(file_path):
                matching.append(finding)
    
    return matching


def filter_by_severity(findings: List[Dict[str, Any]], severity: str) -> List[Dict[str, Any]]:
    """
    Filter findings by severity level (at level or higher).
    
    Args:
        findings: List of finding dictionaries
        severity: Severity threshold (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        
    Returns:
        Filtered list of findings with equal or higher severity
    """
    severity_upper = severity.upper()
    if severity_upper not in SEVERITY_LEVELS:
        raise ValueError(f"Invalid severity: {severity}. Must be one of {list(SEVERITY_LEVELS.keys())}")
    
    threshold = SEVERITY_LEVELS[severity_upper]
    matching = []
    
    for finding in findings:
        finding_severity = finding.get('severity', 'INFO').upper()
        if finding_severity in SEVERITY_LEVELS:
            if SEVERITY_LEVELS[finding_severity] >= threshold:
                matching.append(finding)
    
    return matching


def query_findings(query_type: str, value: str, cache_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Query findings by type and value.
    
    Args:
        query_type: Type of query ('cwe', 'package', 'file', 'severity')
        value: Query value
        cache_dir: Optional path to cache directory
        
    Returns:
        Dictionary with query metadata and matched findings
        
    Raises:
        ValueError: If query_type is invalid
        FileNotFoundError: If findings source not found
    """
    query_type_lower = query_type.lower()
    if not validate_query_type(query_type_lower):
        raise ValueError(f"Invalid query_type: {query_type}. Must be one of {VALID_QUERY_TYPES}")
    
    # Load findings
    try:
        findings = load_findings(cache_dir)
    except FileNotFoundError as e:
        logger.error(f"Failed to load findings: {e}")
        raise
    
    # Apply filter
    if query_type_lower == 'cwe':
        matched = filter_by_cwe(findings, value)
    elif query_type_lower == 'package':
        matched = filter_by_package(findings, value)
    elif query_type_lower == 'file':
        matched = filter_by_file(findings, value)
    elif query_type_lower == 'severity':
        matched = filter_by_severity(findings, value)
    else:
        matched = []
    
    return {
        'query': {
            'type': query_type_lower,
            'value': value,
            'timestamp': datetime.now(timezone.utc).isoformat()
        },
        'results': {
            'total_matched': len(matched),
            'total_findings': len(findings)
        },
        'findings': matched
    }


def format_output(findings: List[Dict[str, Any]], format_type: str = 'json') -> str:
    """
    Format findings for output.
    
    Args:
        findings: List of finding dictionaries
        format_type: Output format ('json', 'csv', 'markdown')
        
    Returns:
        Formatted string
        
    Raises:
        ValueError: If format_type is invalid
    """
    format_lower = format_type.lower()
    if format_lower not in VALID_FORMATS:
        raise ValueError(f"Invalid format: {format_type}. Must be one of {VALID_FORMATS}")
    
    if format_lower == 'json':
        return json.dumps(findings, indent=2, default=str)
    
    elif format_lower == 'csv':
        if not findings:
            return "No findings to export"
        
        output = StringIO()
        # Get all unique keys from all findings
        all_keys: Set[str] = set()
        for finding in findings:
            all_keys.update(finding.keys())
        
        fieldnames = sorted(list(all_keys))
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            writer.writerow(finding)
        
        return output.getvalue()
    
    elif format_lower == 'markdown':
        if not findings:
            return "# Security Findings\n\nNo findings found.\n"
        
        # Group by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'INFO')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(finding)
        
        lines = ["# Security Findings\n"]
        lines.append(f"**Total Findings**: {len(findings)}\n")
        lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}\n\n")
        
        # Sort by severity
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
        for severity in severity_order:
            if severity in by_severity:
                findings_at_level = by_severity[severity]
                lines.append(f"## {severity} ({len(findings_at_level)})\n")
                
                for finding in findings_at_level:
                    lines.append(f"### {finding.get('title', 'Untitled')}\n")
                    lines.append(f"- **Tool**: {finding.get('tool', 'Unknown')}\n")
                    lines.append(f"- **Description**: {finding.get('description', 'N/A')}\n")
                    
                    if finding.get('cwe_id'):
                        lines.append(f"- **CWE**: {finding['cwe_id']}\n")
                    if finding.get('file'):
                        lines.append(f"- **File**: `{finding['file']}`")
                        if finding.get('line'):
                            lines.append(f" (line {finding['line']})")
                        lines.append("\n")
                    if finding.get('package'):
                        lines.append(f"- **Package**: {finding['package']}")
                        if finding.get('version'):
                            lines.append(f" v{finding['version']}")
                        lines.append("\n")
                    
                    lines.append("\n")
        
        return "".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Query security findings API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Query subcommand
    query_parser = subparsers.add_parser('query', help='Query findings')
    query_parser.add_argument(
        '--query-type',
        required=True,
        choices=list(VALID_QUERY_TYPES),
        help='Type of query'
    )
    query_parser.add_argument(
        '--value',
        required=True,
        help='Query value'
    )
    query_parser.add_argument(
        '--cache-dir',
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help='Path to cache directory'
    )
    query_parser.add_argument(
        '--findings-file',
        type=Path,
        help='Path to comprehensive findings JSON file'
    )
    query_parser.add_argument(
        '--format',
        choices=list(VALID_FORMATS),
        default='json',
        help='Output format'
    )
    query_parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (if not specified, outputs to stdout)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute query
        result = query_findings(args.query_type, args.value, args.cache_dir)
        
        # Check if findings were found
        if result['results']['total_matched'] == 0:
            logger.warning(f"No findings matched query: {args.query_type}={args.value}")
            if args.output:
                args.output.write_text(format_output([], args.format))
            else:
                print(format_output([], args.format))
            return 2
        
        # Format findings
        formatted = format_output(result['findings'], args.format)
        
        # Output results
        if args.output:
            args.output.write_text(formatted)
            logger.info(f"Results written to: {args.output}")
        else:
            print(formatted)
        
        logger.info(f"Query successful: {result['results']['total_matched']} findings matched")
        return 0
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
