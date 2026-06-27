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


class FileHandleAuditor(ast.NodeVisitor):
    """AST visitor to find file operations without context managers."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.issues: list[dict] = []
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


def audit_file(filepath: Path) -> list[dict]:
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


def audit_directory(directory: Path) -> dict[Path, list[dict]]:
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


def print_report(results: dict[Path, list[dict]], base_dir: Path):
    """Print a formatted audit report."""
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("FILE HANDLE AUDIT REPORT")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    if not results:
        print("✅ No file handle issues found!")  # codeql[py/clear-text-logging-sensitive-data]
        print()  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    # Calculate statistics
    total_files = len(results)
    total_issues = sum(len(issues) for issues in results.values())
    high_severity = sum(
        1 for issues in results.values()
        for issue in issues
        if issue['severity'] == 'high'
    )

    print("📊 SUMMARY")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   Files with issues: {total_files}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   Total issues: {total_issues}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   High severity: {high_severity}")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    # Sort files by issue count
    sorted_files = sorted(results.items(), key=lambda x: -len(x[1]))

    print("📁 FILES BY SEVERITY (showing top 20)")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    for filepath, issues in sorted_files[:20]:
        relative_path = filepath.relative_to(base_dir)
        high_count = sum(1 for i in issues if i['severity'] == 'high')

        severity_marker = "🔴" if high_count > 0 else "🟡"
        print(f"{severity_marker} {relative_path}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   Issues: {len(issues)} (high: {high_count})")  # codeql[py/clear-text-logging-sensitive-data]

        # Show first 3 issues
        for issue in issues[:3]:
            severity_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢',
                'error': '❌'
            }.get(issue['severity'], '⚪')

            print(f"   {severity_icon} Line {issue['line']}: {issue['type']}")  # codeql[py/clear-text-logging-sensitive-data]
            if len(issue['code']) < 60:
                print(f"      {issue['code']}")  # codeql[py/clear-text-logging-sensitive-data]

        if len(issues) > 3:
            print(f"   ... and {len(issues) - 3} more issues")  # codeql[py/clear-text-logging-sensitive-data]
        print()  # codeql[py/clear-text-logging-sensitive-data]

    if len(sorted_files) > 20:
        print(f"... and {len(sorted_files) - 20} more files with issues")  # codeql[py/clear-text-logging-sensitive-data]
        print()  # codeql[py/clear-text-logging-sensitive-data]

    # Print recommendations
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("🔧 RECOMMENDATIONS")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("1. Convert all open() calls to use 'with' statements:")  # codeql[py/clear-text-logging-sensitive-data]
    print("   BEFORE: f = open('file.txt'); content = f.read(); f.close()")  # codeql[py/clear-text-logging-sensitive-data]
    print("   AFTER:  with open('file.txt') as f: content = f.read()")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("2. For fixtures returning file handles, use yield and cleanup:")  # codeql[py/clear-text-logging-sensitive-data]
    print("   @pytest.fixture")  # codeql[py/clear-text-logging-sensitive-data]
    print("   def open_file():")  # codeql[py/clear-text-logging-sensitive-data]
    print("       f = open('file.txt')")  # codeql[py/clear-text-logging-sensitive-data]
    print("       yield f")  # codeql[py/clear-text-logging-sensitive-data]
    print("       f.close()")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("3. Use pathlib.Path for file operations when possible:")  # codeql[py/clear-text-logging-sensitive-data]
    print("   content = Path('file.txt').read_text()")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("See: .codex/TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md Phase 2")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

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
        print(f"Error: Path does not exist: {test_dir}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    if not test_dir.is_dir():
        print(f"Error: Path is not a directory: {test_dir}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    # Run audit
    print(f"🔍 Auditing {test_dir}...")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    results = audit_directory(test_dir)

    if args.json:
        import json
        # Convert Path keys to strings for JSON serialization
        json_results = {
            str(k): v for k, v in results.items()
        }
        print(json.dumps(json_results, indent=2))  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    # Print report
    issue_count = print_report(results, test_dir)

    # Exit code
    if issue_count > 0:
        print(f"⚠️  Found {issue_count} file handle issues")  # codeql[py/clear-text-logging-sensitive-data]
        return 1
    print("✅ No issues found")  # codeql[py/clear-text-logging-sensitive-data]
    return 0


if __name__ == '__main__':
    sys.exit(main())
