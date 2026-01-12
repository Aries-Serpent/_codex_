#!/usr/bin/env python3
"""CI Failure Analyzer - Analyzes CI failure logs and suggests automated fixes"""

import click
import json
import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class FailureAnalysis:
    """Analysis result for a CI failure"""
    fix_available: bool
    fix_type: str
    fix_params: Dict
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
                'regex': r'(ruff check|mypy).+error',
                'fix_type': 'python_lint',
                'confidence': 85,
                'description': 'Python linting issue',
                'fix': 'Run ruff --fix'
            },
        }
    
    def analyze(self, log_file: Path) -> FailureAnalysis:
        """Analyze failure log"""
        log_content = log_file.read_text()
        
        for pattern_name, pattern_info in self.patterns.items():
            if re.search(pattern_info['regex'], log_content, re.IGNORECASE):
                return FailureAnalysis(
                    fix_available=True,
                    fix_type=pattern_info['fix_type'],
                    fix_params={},
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
