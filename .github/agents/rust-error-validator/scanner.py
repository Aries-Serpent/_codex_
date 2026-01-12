#!/usr/bin/env python3
"""Rust Error Handling Validator - Scans for panic risks"""
import click
import re
from pathlib import Path
from typing import List
from dataclasses import dataclass

@dataclass
class Finding:
    file: str
    line: int
    severity: str
    issue: str

class RustErrorScanner:
    def scan_file(self, filepath: Path) -> List[Finding]:
        findings = []
        try:
            lines = filepath.read_text().splitlines()
            for i, line in enumerate(lines, 1):
                context_start_5 = max(0, i - 5)
                context_lines_5 = lines[context_start_5:i]
                if '.unwrap()' in line and not any('#[test]' in l for l in context_lines_5):
                    context_start_10 = max(0, i - 10)
                    context_lines_10 = lines[context_start_10:i]
                    severity = "high" if any(
                        marker in l
                        for l in context_lines_10
                        for marker in ['#[pyfunction]', '#[pymethods]']
                    ) else "medium"
                    findings.append(Finding(
                        str(filepath),
                        i,
                        severity,
                        f"unwrap() can panic in code: {line.strip()} - use PyResult or unwrap_or_else",
                    ))
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
        return findings

@click.command()
@click.option('--dir', type=click.Path(exists=True), required=True)
def scan(dir):
    scanner = RustErrorScanner()
    findings = []
    for f in Path(dir).rglob('*.rs'):
        findings.extend(scanner.scan_file(f))
    for f in findings:
        click.echo(f"{f.file}:{f.line} [{f.severity.upper()}] {f.issue}")
    click.echo(f"\nTotal: {len(findings)} findings")

if __name__ == '__main__':
    scan()
