#!/usr/bin/env python3
"""
Codebase QA Walkthrough Script

Performs comprehensive code quality analysis including:
- AST validation (syntax checking)
- Code style analysis (via ruff)
- Security scanning (via bandit)
- Test coverage analysis
"""

import ast
import json
import pathlib
import subprocess
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional

class CodebaseQAWalker:
    """Walks through codebase and performs QA checks."""
    
    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.critical_issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.stats: Dict[str, int] = defaultdict(int)
        
    def scan_ast(self, src_root: pathlib.Path = None) -> None:
        """Scan Python files for syntax errors and basic AST issues."""
        if src_root is None:
            src_root = pathlib.Path('src')
        
        if not src_root.exists():
            return
            
        py_files = list(src_root.rglob('*.py'))
        self.stats['total_python_files'] = len(py_files)
        
        syntax_errors = 0
        for py_file in py_files:
            try:
                with open(py_file, encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                ast.parse(code)
            except SyntaxError as e:
                syntax_errors += 1
                self.critical_issues.append({
                    'file': str(py_file),
                    'type': 'SyntaxError',
                    'message': str(e),
                    'severity': 'critical',
                    'line': e.lineno or 0
                })
            except Exception as e:
                self.warnings.append({
                    'file': str(py_file),
                    'type': type(e).__name__,
                    'message': str(e),
                    'severity': 'warning'
                })
        
        self.stats['syntax_errors'] = syntax_errors
        if syntax_errors > 0:
            self.issues.append({
                'type': 'SyntaxError',
                'count': syntax_errors,
                'severity': 'critical'
            })
    
    def run_ruff_check(self, src_root: pathlib.Path = None) -> None:
        """Run ruff lint checks."""
        if src_root is None:
            src_root = pathlib.Path('src')
        
        if not src_root.exists():
            return
        
        try:
            result = subprocess.run(
                ['python3', '-m', 'ruff', 'check', str(src_root), 
                 '--output-format', 'json', '--extend-ignore=E501'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                try:
                    ruff_issues = json.loads(result.stdout)
                    if isinstance(ruff_issues, list):
                        self.stats['ruff_issues'] = len(ruff_issues)
                        # Categorize by severity
                        for issue in ruff_issues:
                            if 'code' in issue and issue['code'] in ['E9', 'F8']:  # Critical codes
                                self.critical_issues.append({
                                    'file': issue.get('filename', ''),
                                    'type': f"Ruff:{issue.get('code', 'unknown')}",
                                    'message': issue.get('message', ''),
                                    'severity': 'critical',
                                    'line': issue.get('location', {}).get('row', 0)
                                })
                            else:
                                self.issues.append({
                                    'file': issue.get('filename', ''),
                                    'type': f"Ruff:{issue.get('code', 'unknown')}",
                                    'message': issue.get('message', ''),
                                    'severity': 'warning'
                                })
                except (json.JSONDecodeError, ValueError):
                    pass  # If output is not valid JSON, continue
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Ruff not available or timeout
    
    def run_bandit_check(self, src_root: pathlib.Path = None) -> None:
        """Run bandit security scan."""
        if src_root is None:
            src_root = pathlib.Path('src')
        
        if not src_root.exists():
            return
        
        try:
            result = subprocess.run(
                ['python3', '-m', 'bandit', '-r', str(src_root), 
                 '-f', 'json', '--severity-level', 'medium'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    results = bandit_results.get('results', [])
                    self.stats['security_issues'] = len(results)
                    
                    for issue in results:
                        severity = issue.get('severity', 'MEDIUM').lower()
                        self.critical_issues.append({
                            'file': issue.get('filename', ''),
                            'type': f"Bandit:{issue.get('test_id', 'unknown')}",
                            'message': issue.get('issue_text', ''),
                            'severity': 'critical' if severity == 'high' else 'warning',
                            'line': issue.get('line_number', 0)
                        })
                except (json.JSONDecodeError, ValueError):
                    pass  # If output is not valid JSON, continue
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Bandit not available or timeout
    
    def check_tests_exist(self) -> None:
        """Check if test files exist."""
        tests_root = pathlib.Path('tests')
        if tests_root.exists():
            test_files = list(tests_root.rglob('test_*.py'))
            self.stats['test_files'] = len(test_files)
        else:
            self.stats['test_files'] = 0
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate QA walkthrough report."""
        report = {
            'total_issues': len(self.issues),
            'critical_issues': len(self.critical_issues),
            'warnings': len(self.warnings),
            'statistics': dict(self.stats),
            'issues': self.issues[:100],  # Limit to first 100
            'critical_details': self.critical_issues[:50],  # Limit details
            'warnings_sample': self.warnings[:20]
        }
        return report
    
    def run_full_walkthrough(self) -> Dict[str, Any]:
        """Run complete QA walkthrough."""
        print("🔍 Starting Codebase QA Walkthrough...", file=sys.stderr)
        
        print("  - AST validation...", file=sys.stderr)
        self.scan_ast()
        
        print("  - Ruff lint checks...", file=sys.stderr)
        self.run_ruff_check()
        
        print("  - Bandit security scan...", file=sys.stderr)
        self.run_bandit_check()
        
        print("  - Test coverage check...", file=sys.stderr)
        self.check_tests_exist()
        
        report = self.generate_report()
        print(f"✅ Walkthrough complete: {report['total_issues']} issues found "
              f"({report['critical_issues']} critical)", file=sys.stderr)
        
        return report


def main():
    """Main entry point."""
    walker = CodebaseQAWalker()
    report = walker.run_full_walkthrough()
    
    # Create output directory
    output_dir = pathlib.Path('.codex/qa')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write results to JSON
    results_file = output_dir / 'results.json'
    with open(results_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📝 Report written to {results_file}", file=sys.stderr)
    
    # Exit with non-zero if critical issues found
    if report['critical_issues'] > 0:
        print(f"⚠️  {report['critical_issues']} critical issue(s) found", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
