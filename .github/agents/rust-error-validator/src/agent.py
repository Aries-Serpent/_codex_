#!/usr/bin/env python3
"""
Rust Error Validator Agent

Scans Rust code for unsafe error handling patterns that can cause panics,
particularly focusing on .unwrap() calls in PyO3 bindings.

Usage:
    python -m rust_error_validator.agent --dir ./rust_src
"""

import click
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml


@dataclass
class Finding:
    """Represents a detected error handling issue."""
    file: str
    line: int
    severity: str
    issue: str
    suggestion: str = ""


class RustErrorValidator:
    """
    Validates Rust error handling patterns to prevent panics.
    
    Focuses on:
    - .unwrap() calls outside tests
    - Missing error propagation in PyO3 functions
    - Panic-prone patterns in public APIs
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize validator with optional config."""
        self.config = self._load_config(config_path)
        self.patterns = self._compile_patterns()
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load validator configuration."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'version': '1.0.0',
            'enabled': True,
            'check_unwrap': True,
            'check_expect': True,
            'check_panic': True,
            'ignore_test_code': True,
            'pyo3_strict_mode': True,
            'severity_levels': {
                'pyo3_unwrap': 'high',
                'public_unwrap': 'high',
                'private_unwrap': 'medium',
                'test_unwrap': 'low',
            }
        }
    
    def _compile_patterns(self) -> Dict:
        """Compile regex patterns for detection."""
        return {
            'unwrap': re.compile(r'\.unwrap\(\)'),
            'expect': re.compile(r'\.expect\('),
            'panic': re.compile(r'panic!\('),
            'pyo3_function': re.compile(r'#\[pyfunction\]'),
            'pyo3_methods': re.compile(r'#\[pymethods\]'),
            'test_marker': re.compile(r'#\[test\]|#\[cfg\(test\)\]'),
        }
    
    def scan_file(self, filepath: Path) -> List[Finding]:
        """
        Scan a single Rust file for error handling issues.
        
        Args:
            filepath: Path to .rs file to scan
            
        Returns:
            List of Finding objects for detected issues
        """
        findings = []
        
        try:
            lines = filepath.read_text().splitlines()
            
            for i, line in enumerate(lines, 1):
                # Get context lines for analysis
                context_start_5 = max(0, i - 6)
                context_lines_5 = lines[context_start_5:i-1]
                
                context_start_10 = max(0, i - 11)
                context_lines_10 = lines[context_start_10:i-1]
                
                # Check if in test code
                in_test = any(
                    self.patterns['test_marker'].search(l) 
                    for l in context_lines_10
                )
                
                # Skip test code if configured
                if in_test and self.config['ignore_test_code']:
                    continue
                
                # Check for .unwrap() calls
                if self.config['check_unwrap'] and self.patterns['unwrap'].search(line):
                    # Determine severity based on context
                    in_pyo3 = any(
                        self.patterns['pyo3_function'].search(l) or 
                        self.patterns['pyo3_methods'].search(l)
                        for l in context_lines_10
                    )
                    
                    severity = "high" if in_pyo3 else "medium"
                    
                    findings.append(Finding(
                        file=str(filepath),
                        line=i,
                        severity=severity,
                        issue=f"unwrap() can panic - found in: {line.strip()}",
                        suggestion="Use PyResult for PyO3 functions or unwrap_or_else() for graceful handling"
                    ))
                
                # Check for .expect() calls
                if self.config['check_expect'] and self.patterns['expect'].search(line):
                    findings.append(Finding(
                        file=str(filepath),
                        line=i,
                        severity="medium",
                        issue=f"expect() can panic - found in: {line.strip()}",
                        suggestion="Consider using PyResult or proper error handling"
                    ))
                
                # Check for panic!() macros
                if self.config['check_panic'] and self.patterns['panic'].search(line):
                    findings.append(Finding(
                        file=str(filepath),
                        line=i,
                        severity="high",
                        issue=f"explicit panic found - {line.strip()}",
                        suggestion="Replace with Result<T, E> error propagation"
                    ))
                    
        except Exception as e:
            click.echo(f"Error scanning {filepath}: {e}", err=True)
        
        return findings
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Finding]:
        """
        Scan a directory for Rust files and validate error handling.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            List of all findings across all scanned files
        """
        all_findings = []
        
        pattern = '**/*.rs' if recursive else '*.rs'
        for rust_file in directory.glob(pattern):
            findings = self.scan_file(rust_file)
            all_findings.extend(findings)
        
        return all_findings
    
    def generate_report(self, findings: List[Finding]) -> Dict:
        """
        Generate a summary report of all findings.
        
        Args:
            findings: List of Finding objects
            
        Returns:
            Dictionary with summary statistics and grouped findings
        """
        severity_counts = {
            'high': sum(1 for f in findings if f.severity == 'high'),
            'medium': sum(1 for f in findings if f.severity == 'medium'),
            'low': sum(1 for f in findings if f.severity == 'low'),
        }
        
        return {
            'total_findings': len(findings),
            'severity_breakdown': severity_counts,
            'findings_by_severity': {
                'high': [f for f in findings if f.severity == 'high'],
                'medium': [f for f in findings if f.severity == 'medium'],
                'low': [f for f in findings if f.severity == 'low'],
            },
            'unique_files': len(set(f.file for f in findings)),
        }


@click.command()
@click.option('--dir', type=click.Path(exists=True), required=True, help='Directory to scan')
@click.option('--config', type=click.Path(exists=True), help='Config file path')
@click.option('--recursive/--no-recursive', default=True, help='Scan subdirectories')
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--verbose', is_flag=True, help='Verbose output')
def main(dir, config, recursive, format, verbose):
    """Rust Error Validator CLI"""
    validator = RustErrorValidator(Path(config) if config else None)
    
    directory = Path(dir)
    findings = validator.scan_directory(directory, recursive=recursive)
    
    if format == 'json':
        import json
        report = validator.generate_report(findings)
        click.echo(json.dumps(report, indent=2, default=str))
    else:
        # Text format output
        for f in findings:
            severity_color = {
                'high': 'red',
                'medium': 'yellow',
                'low': 'blue'
            }.get(f.severity, 'white')
            
            click.secho(
                f"{f.file}:{f.line} [{f.severity.upper()}] {f.issue}",
                fg=severity_color
            )
            if verbose and f.suggestion:
                click.echo(f"  → Suggestion: {f.suggestion}")
        
        # Print summary
        report = validator.generate_report(findings)
        click.echo(f"\nTotal: {report['total_findings']} findings")
        click.echo(f"  High: {report['severity_breakdown']['high']}")
        click.echo(f"  Medium: {report['severity_breakdown']['medium']}")
        click.echo(f"  Low: {report['severity_breakdown']['low']}")
        click.echo(f"Files affected: {report['unique_files']}")


if __name__ == '__main__':
    main()
