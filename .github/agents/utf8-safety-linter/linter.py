#!/usr/bin/env python3
"""UTF-8 String Safety Linter"""
import click
import re
import yaml
from pathlib import Path

class UTF8SafetyLinter:
    UNSAFE_PATTERNS = [
        (r'\.slice\s*\(\s*\d+\s*,\s*\d+\s*\)', 'Direct slice without boundary check'),
        (r'\.substring\s*\(\s*\d+\s*,\s*\d+\s*\)', 'Direct substring without boundary check'),
        (r'\[(\w+)\](?!\s*=)', 'Direct string indexing'),
    ]
    
    def scan_file(self, filepath: Path):
        findings = []
        try:
            content = filepath.read_text()
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                for pattern, message in self.UNSAFE_PATTERNS:
                    if re.search(pattern, line):
                        # Check if it has safeTruncate or surrogate check nearby
                        context = '\n'.join(lines[max(0,i-5):min(len(lines),i+5)])
                        if 'charCodeAt' not in context and '0xDC00' not in context:
                            findings.append((filepath, i, message, line.strip()))
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
        return findings

@click.command()
@click.option('--file', type=click.Path(exists=True))
@click.option('--dir', type=click.Path(exists=True))
def scan(file, dir):
    linter = UTF8SafetyLinter()
    findings = []
    
    if file:
        findings = linter.scan_file(Path(file))
    elif dir:
        for f in Path(dir).rglob('*.{js,ts,yml,yaml}'):
            findings.extend(linter.scan_file(f))
    
    for f, line, msg, code in findings:
        click.echo(f"{f}:{line} [WARNING] {msg}")
        click.echo(f"  Code: {code}")
    
    click.echo(f"\nTotal: {len(findings)} potential UTF-8 safety issues")

if __name__ == '__main__':
    scan()
