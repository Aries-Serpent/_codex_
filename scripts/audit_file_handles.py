#!/usr/bin/env python3
"""Audit test files for file handle management issues.

This script identifies file operations that don't use context managers,
which can lead to file handle leaks and resource exhaustion.

Related: PR #3178 - 744 test failures, resource exhaustion at 57% completion
See: .codex/COMPLETE_TEST_FAILURE_ANALYSIS_744_ISSUES.md

Usage:
    python scripts/audit_file_handles.py
    python scripts/audit_file_handles.py tests/specific/module/

Output:
    - List of files with file handle issues
    - Specific line numbers and problematic code
    - Severity ranking by issue count
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List


class FileHandleAuditor(ast.NodeVisitor):
    """AST visitor to find file operations without context managers."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.issues: List[Dict] = []
        self.in_with_statement = False
        self.with_depth = 0
        self.in_context_manager_method = False
        self.current_function_name = None

    def visit_With(self, node):
        """Track when we're inside a 'with' statement."""
        self.with_depth += 1
        self.generic_visit(node)
        self.with_depth -= 1

    def visit_FunctionDef(self, node):
        """Track when we're inside context manager methods."""
        prev_function = self.current_function_name
        prev_in_cm = self.in_context_manager_method

        self.current_function_name = node.name
        # Check if this is a context manager method or cleanup method
        if node.name in ('__enter__', '__exit__', '__del__', 'close', '_open', '_close'):
            self.in_context_manager_method = True

        self.generic_visit(node)

        self.current_function_name = prev_function
        self.in_context_manager_method = prev_in_cm

    def visit_Call(self, node):
        """Check for open() calls outside 'with' statements."""
        # Check for open() function
        if isinstance(node.func, ast.Name) and node.func.id == 'open':
            # Allow open() in context manager methods and with statements
            if self.with_depth == 0 and not self.in_context_manager_method:
                self.issues.append({
                    'line': node.lineno,
                    'col': node.col_offset,
                    'type': 'open_without_context',
                    'code': ast.unparse(node) if hasattr(ast, 'unparse') else '<code>',
                    'severity': 'high'
                })

        # Check for file() function (deprecated but sometimes used)
        elif isinstance(node.func, ast.Name) and node.func.id == 'file':
            self.issues.append({
                'line': node.lineno,
                'col': node.col_offset,
                'type': 'deprecated_file',
                'code': ast.unparse(node) if hasattr(ast, 'unparse') else '<code>',
                'severity': 'medium'
            })

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Check for .open() method calls."""
        if isinstance(node, ast.Attribute) and node.attr == 'open':
            # This might be a file open on an object
            parent = node.value
            if isinstance(parent, ast.Name):
                # Check if it looks like a file operation
                if any(keyword in parent.id.lower() for keyword in ['file', 'path', 'stream']):
                    if self.with_depth == 0:
                        self.issues.append({
                            'line': node.lineno,
                            'col': node.col_offset,
                            'type': 'method_open_without_context',
                            'code': f"{parent.id}.open(...)",
                            'severity': 'medium'
                        })

        self.generic_visit(node)


def audit_file(filepath: Path) -> List[Dict]:
    """Audit a single Python file for file handle issues."""
    try:
        with open(filepath) as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            return [{
                'line': e.lineno or 0,
                'col': 0,
                'type': 'syntax_error',
                'code': str(e),
                'severity': 'error'
            }]

        auditor = FileHandleAuditor(filepath)
        auditor.visit(tree)
        return auditor.issues

    except Exception as e:
        return [{
            'line': 0,
            'col': 0,
            'type': 'audit_error',
            'code': str(e),
            'severity': 'error'
        }]


def audit_directory(directory: Path) -> Dict[Path, List[Dict]]:
    """Audit all Python files in a directory."""
    results = {}

    for pyfile in directory.rglob('*.py'):
        # Skip __pycache__ and .pyc files
        if '__pycache__' in str(pyfile):
            continue

        issues = audit_file(pyfile)
        if issues:
            results[pyfile] = issues

    return results


def print_report(results: Dict[Path, List[Dict]], base_dir: Path):
    """Print a formatted audit report."""
    print("=" * 80)
    print("FILE HANDLE AUDIT REPORT")
    print("=" * 80)
    print()

    if not results:
        print("✅ No file handle issues found!")
        print()
        return 0

    # Calculate statistics
    total_files = len(results)
    total_issues = sum(len(issues) for issues in results.values())
    high_severity = sum(
        1 for issues in results.values()
        for issue in issues
        if issue['severity'] == 'high'
    )

    print("📊 SUMMARY")
    print(f"   Files with issues: {total_files}")
    print(f"   Total issues: {total_issues}")
    print(f"   High severity: {high_severity}")
    print()

    # Sort files by issue count
    sorted_files = sorted(results.items(), key=lambda x: -len(x[1]))

    print("📁 FILES BY SEVERITY (showing top 20)")
    print()

    for filepath, issues in sorted_files[:20]:
        relative_path = filepath.relative_to(base_dir)
        high_count = sum(1 for i in issues if i['severity'] == 'high')

        severity_marker = "🔴" if high_count > 0 else "🟡"
        print(f"{severity_marker} {relative_path}")
        print(f"   Issues: {len(issues)} (high: {high_count})")

        # Show first 3 issues
        for issue in issues[:3]:
            severity_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢',
                'error': '❌'
            }.get(issue['severity'], '⚪')

            print(f"   {severity_icon} Line {issue['line']}: {issue['type']}")
            if len(issue['code']) < 60:
                print(f"      {issue['code']}")

        if len(issues) > 3:
            print(f"   ... and {len(issues) - 3} more issues")
        print()

    if len(sorted_files) > 20:
        print(f"... and {len(sorted_files) - 20} more files with issues")
        print()

    # Print recommendations
    print("=" * 80)
    print("🔧 RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("1. Convert all open() calls to use 'with' statements:")
    print("   BEFORE: f = open('file.txt'); content = f.read(); f.close()")
    print("   AFTER:  with open('file.txt') as f: content = f.read()")
    print()
    print("2. For fixtures returning file handles, use yield and cleanup:")
    print("   @pytest.fixture")
    print("   def open_file():")
    print("       f = open('file.txt')")
    print("       yield f")
    print("       f.close()")
    print()
    print("3. Use pathlib.Path for file operations when possible:")
    print("   content = Path('file.txt').read_text()")
    print()
    print("See: .codex/TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md Phase 2")
    print()

    return total_issues


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit test files for file handle management issues"
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='tests',
        help='Path to test directory (default: tests/)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    test_dir = Path(args.path)
    if not test_dir.exists():
        print(f"Error: Path does not exist: {test_dir}", file=sys.stderr)
        return 1

    if not test_dir.is_dir():
        print(f"Error: Path is not a directory: {test_dir}", file=sys.stderr)
        return 1

    # Run audit
    print(f"🔍 Auditing {test_dir}...")
    print()

    results = audit_directory(test_dir)

    if args.json:
        import json
        # Convert Path keys to strings for JSON serialization
        json_results = {
            str(k): v for k, v in results.items()
        }
        print(json.dumps(json_results, indent=2))
        return 0

    # Print report
    issue_count = print_report(results, test_dir)

    # Exit code
    if issue_count > 0:
        print(f"⚠️  Found {issue_count} file handle issues")
        return 1
    print("✅ No issues found")
    return 0


if __name__ == '__main__':
    sys.exit(main())
