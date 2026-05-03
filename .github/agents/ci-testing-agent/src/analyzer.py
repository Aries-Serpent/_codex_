#!/usr/bin/env python3
"""CI Failure Analyzer - Analyzes CI failure logs and suggests automated fixes"""

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click


@dataclass
class FailureAnalysis:
    """Analysis result for a CI failure"""
    fix_available: bool
    fix_type: str
    fix_params: dict
    confidence: int
    failure_type: str
    failure_description: str
    fix_description: str
    pattern_matched: Optional[str] = None
    timestamp: Optional[str] = None


class CIFailureAnalyzer:
    """Analyzes CI failure logs and suggests fixes"""

    def __init__(self):
        self.patterns = {
            'rust_formatting': {
                'regex': r'Diff in .+\.rs',
                'fix_type': 'rust_format',
                'confidence': 95,
                'description': 'Rust formatting issue',
                'fix': 'Run cargo fmt --all'
            },
            'python_linting': {
                'regex': r'(ruff check|ruff.*error|mypy.*error)',
                'fix_type': 'python_lint',
                'confidence': 85,
                'description': 'Python linting issue',
                'fix': 'Run ruff --fix'
            },
            'test_timeout': {
                'regex': r'(TIMEOUT|timed out after|TimeoutError)',
                'fix_type': 'increase_timeout',
                'confidence': 70,
                'description': 'Test timeout detected',
                'fix': 'Increase timeout value'
            },
            'import_error': {
                'regex': r"(ModuleNotFoundError|ImportError|No module named '[^']+')",
                'fix_type': 'add_dependency',
                'confidence': 80,
                'description': 'Missing Python dependency',
                'fix': 'Add missing package to requirements'
            },
            'cache_corruption': {
                'regex': r'(cache.+corrupt|failed to restore cache|cache.*invalid)',
                'fix_type': 'clear_cache',
                'confidence': 90,
                'description': 'Cache corruption detected',
                'fix': 'Clear and rebuild cache'
            },
            'cargo_lock_conflict': {
                'regex': r'(Cargo\.lock.*conflict|failed to update.*Cargo\.lock)',
                'fix_type': 'cargo_update',
                'confidence': 85,
                'description': 'Cargo.lock conflict',
                'fix': 'Update Cargo.lock'
            },
            'network_timeout': {
                'regex': r'(connection timed out|network.*timeout|failed to connect)',
                'fix_type': 'retry',
                'confidence': 75,
                'description': 'Network timeout',
                'fix': 'Retry with backoff'
            },
            'disk_space': {
                'regex': r'(no space left|disk.*full|ENOSPC)',
                'fix_type': 'cleanup_disk',
                'confidence': 95,
                'description': 'Disk space issue',
                'fix': 'Clean up disk space'
            },
        }

    def analyze(self, log_file: Path) -> FailureAnalysis:
        """Analyze failure log and extract fix parameters"""
        log_content = log_file.read_text()

        for pattern_name, pattern_info in self.patterns.items():
            if re.search(pattern_info['regex'], log_content, re.IGNORECASE):
                fix_params = self._extract_params(log_content, pattern_info)
                return FailureAnalysis(
                    fix_available=True,
                    fix_type=pattern_info['fix_type'],
                    fix_params=fix_params,
                    confidence=pattern_info['confidence'],
                    failure_type=pattern_name,
                    failure_description=pattern_info['description'],
                    fix_description=pattern_info['fix'],
                    pattern_matched=pattern_name,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )

        return FailureAnalysis(
            fix_available=False,
            fix_type='unknown',
            fix_params={},
            confidence=0,
            failure_type='unknown',
            failure_description='Unable to classify failure',
            fix_description='Manual intervention required',
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _extract_params(self, log: str, pattern: dict) -> dict:
        """Extract fix parameters from log based on fix type"""
        params = {}

        if pattern['fix_type'] == 'rust_format':
            # Extract file names that need formatting
            files = re.findall(r'Diff in ([^\s:]+\.rs)', log)
            params['files'] = files

        elif pattern['fix_type'] == 'increase_timeout':
            # Extract current timeout value
            match = re.search(r'timed out after (\d+)', log)
            if match:
                current = int(match.group(1))
                params['current_timeout'] = current
                params['suggested_timeout'] = current * 2
            else:
                params['current_timeout'] = 60
                params['suggested_timeout'] = 120

        elif pattern['fix_type'] == 'add_dependency':
            # Extract missing module name
            match = re.search(r"No module named '([^']+)'", log)
            if match:
                params['missing_module'] = match.group(1)

        elif pattern['fix_type'] == 'cargo_update':
            # Extract package name if available
            match = re.search(r'(failed to update.*`([^`]+)`|package `([^`]+)`)', log)
            if match:
                params['package'] = match.group(2) or match.group(3)

        return params


@click.command()
@click.option('--log-file', type=click.Path(exists=True), required=True)
@click.option('--output-json', type=click.Path(), required=True)
def main(log_file, output_json):
    """Analyze CI failure log"""
    analyzer = CIFailureAnalyzer()
    analysis = analyzer.analyze(Path(log_file))
    Path(output_json).write_text(json.dumps(asdict(analysis), indent=2))
    click.echo(f"Analysis complete: {output_json}")


if __name__ == '__main__':
    main()
