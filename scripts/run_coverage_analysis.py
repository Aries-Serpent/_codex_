#!/usr/bin/env python3
"""
Coverage Analysis Runner

Generates comprehensive coverage reports for the test suite.
Outputs HTML, JSON, and XML formats for different use cases.

Usage:
    python scripts/run_coverage_analysis.py
    python scripts/run_coverage_analysis.py --target agents
    python scripts/run_coverage_analysis.py --html-only
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse


class CoverageAnalyzer:
    """Analyzes test coverage and generates reports."""
    
    def __init__(self, target_dir: str = "agents", output_dir: str = "coverage_reports"):
        self.target_dir = target_dir
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def run_coverage(self, test_path: str = "tests/") -> bool:
        """Run pytest with coverage."""
        print(f"\n{'='*80}")
        print(f"Running Coverage Analysis")
        print(f"{'='*80}")
        print(f"Target: {self.target_dir}")
        print(f"Tests: {test_path}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            f"--cov={self.target_dir}",
            "--cov-report=html:coverage_reports/html",
            "--cov-report=json:coverage_reports/coverage.json",
            "--cov-report=xml:coverage_reports/coverage.xml",
            "--cov-report=term-missing",
            "-v",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running coverage: {e}")
            return False
    
    def analyze_json_report(self) -> Dict[str, Any]:
        """Analyze JSON coverage report."""
        json_path = self.output_dir / "coverage.json"
        
        if not json_path.exists():
            print(f"Warning: {json_path} not found")
            return {}
        
        with open(json_path) as f:
            data = json.load(f)
        
        analysis = {
            'total_coverage': data.get('totals', {}).get('percent_covered', 0),
            'total_statements': data.get('totals', {}).get('num_statements', 0),
            'covered_statements': data.get('totals', {}).get('covered_lines', 0),
            'missing_statements': data.get('totals', {}).get('missing_lines', 0),
            'files': {}
        }
        
        # Analyze per-file coverage
        for filepath, file_data in data.get('files', {}).items():
            if self.target_dir in filepath:
                summary = file_data.get('summary', {})
                analysis['files'][filepath] = {
                    'coverage': summary.get('percent_covered', 0),
                    'statements': summary.get('num_statements', 0),
                    'missing': summary.get('missing_lines', 0),
                    'covered': summary.get('covered_lines', 0)
                }
        
        return analysis
    
    def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        report = []
        report.append("\n" + "="*80)
        report.append("COVERAGE ANALYSIS SUMMARY")
        report.append("="*80)
        
        # Overall statistics
        report.append(f"\nOverall Coverage: {analysis['total_coverage']:.2f}%")
        report.append(f"Total Statements: {analysis['total_statements']}")
        report.append(f"Covered: {analysis['covered_statements']}")
        report.append(f"Missing: {analysis['missing_statements']}")
        
        # Per-file breakdown
        report.append(f"\n{'='*80}")
        report.append("PER-FILE COVERAGE")
        report.append("="*80)
        
        files = sorted(
            analysis['files'].items(),
            key=lambda x: x[1]['coverage']
        )
        
        for filepath, stats in files:
            filename = Path(filepath).name
            coverage = stats['coverage']
            status = "✅" if coverage >= 80 else "🔄" if coverage >= 50 else "⚠️"
            
            report.append(f"\n{status} {filename}")
            report.append(f"   Coverage: {coverage:.1f}%")
            report.append(f"   Statements: {stats['statements']} "
                         f"(Covered: {stats['covered']}, Missing: {stats['missing']})")
        
        # Files needing attention
        report.append(f"\n{'='*80}")
        report.append("FILES NEEDING ATTENTION (<80% coverage)")
        report.append("="*80)
        
        low_coverage = [(f, s) for f, s in files if s['coverage'] < 80]
        if low_coverage:
            for filepath, stats in low_coverage:
                report.append(f"\n⚠️  {Path(filepath).name}: {stats['coverage']:.1f}%")
        else:
            report.append("\n✅ All files have ≥80% coverage!")
        
        return "\n".join(report)
    
    def generate_badge_data(self, coverage: float) -> str:
        """Generate badge color based on coverage."""
        if coverage >= 90:
            color = "brightgreen"
        elif coverage >= 80:
            color = "green"
        elif coverage >= 70:
            color = "yellowgreen"
        elif coverage >= 60:
            color = "yellow"
        elif coverage >= 50:
            color = "orange"
        else:
            color = "red"
        
        return f"![Coverage](https://img.shields.io/badge/coverage-{coverage:.0f}%25-{color})"
    
    def save_summary(self, analysis: Dict[str, Any]):
        """Save analysis summary to file."""
        summary = self.generate_summary_report(analysis)
        
        summary_path = self.output_dir / "summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(summary)
        print(f"\n✅ Summary saved to: {summary_path}")
        
        # Generate badge
        badge = self.generate_badge_data(analysis['total_coverage'])
        badge_path = self.output_dir / "badge.md"
        with open(badge_path, 'w') as f:
            f.write(badge)
        print(f"✅ Badge markdown saved to: {badge_path}")
    
    def run_full_analysis(self, test_path: str = "tests/"):
        """Run complete coverage analysis pipeline."""
        print("Starting full coverage analysis...")
        
        # Run coverage
        success = self.run_coverage(test_path)
        
        if not success:
            print("⚠️  Coverage run had issues, but continuing with analysis...")
        
        # Analyze results
        analysis = self.analyze_json_report()
        
        if analysis:
            # Generate and save summary
            self.save_summary(analysis)
            
            print(f"\n{'='*80}")
            print("Coverage reports generated:")
            print(f"  - HTML: {self.output_dir / 'html' / 'index.html'}")
            print(f"  - JSON: {self.output_dir / 'coverage.json'}")
            print(f"  - XML: {self.output_dir / 'coverage.xml'}")
            print(f"  - Summary: {self.output_dir / 'summary.txt'}")
            print(f"  - Badge: {self.output_dir / 'badge.md'}")
            print("="*80)
        else:
            print("⚠️  No coverage data found. Tests may not have run successfully.")


def main():
    parser = argparse.ArgumentParser(description='Run coverage analysis')
    parser.add_argument('--target', default='agents', help='Target directory to analyze')
    parser.add_argument('--tests', default='tests/', help='Test directory')
    parser.add_argument('--output', default='coverage_reports', help='Output directory')
    parser.add_argument('--html-only', action='store_true', help='Generate HTML report only')
    
    args = parser.parse_args()
    
    analyzer = CoverageAnalyzer(
        target_dir=args.target,
        output_dir=args.output
    )
    
    if args.html_only:
        print("Running coverage for HTML report only...")
        analyzer.run_coverage(args.tests)
    else:
        analyzer.run_full_analysis(args.tests)


if __name__ == '__main__':
    main()
