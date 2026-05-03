#!/usr/bin/env python3
"""Analyze test suite for potential mock-related issues."""

import ast
from pathlib import Path


class MockPatternAnalyzer(ast.NodeVisitor):
    """AST visitor to detect problematic mock patterns."""

    def __init__(self):
        self.issues = []
        self.current_file = None
        self.fixture_names = set()

    def visit_FunctionDef(self, node):
        # Check for pytest fixtures
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'fixture':
                self.fixture_names.add(node.name)
                # Analyze fixture body for side_effect pattern
                self._check_fixture_body(node)

        # Check test functions using MagicMock
        if node.name.startswith('test_'):
            self._check_test_function(node)

        self.generic_visit(node)

    def _check_fixture_body(self, node):
        """Check fixture for side_effect exhaustion pattern."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute) and target.attr == 'side_effect':
                        # Check if side_effect value is a list
                        if isinstance(stmt.value, ast.List):
                            self.issues.append({
                                'file': self.current_file,
                                'line': stmt.lineno,
                                'type': 'side_effect_list',
                                'severity': 'HIGH',
                                'message': 'Fixture uses side_effect with list - may cause StopIteration'
                            })

    def _check_test_function(self, node):
        """Check test function for JSON serialization of mocks."""
        try:
            # ast.unparse() was introduced in Python 3.9
            if hasattr(ast, 'unparse'):
                source = ast.unparse(node)
            else:
                # Fallback for Python < 3.9: simple heuristic check
                # Check if both patterns exist in the function's code
                source_lines = []
                for child in ast.walk(node):
                    if getattr(child, 'id', None) == 'MagicMock':
                        source_lines.append('MagicMock')
                    if getattr(child, 'attr', None) == 'dumps':
                        source_lines.append('json.dumps')
                source = ' '.join(source_lines)

            if 'json.dumps' in source and 'MagicMock' in source:
                self.issues.append({
                    'file': self.current_file,
                    'line': node.lineno,
                    'type': 'mock_serialization',
                    'severity': 'MEDIUM',
                    'message': 'Test may attempt JSON serialization of MagicMock'
                })
        except Exception:
            # If analysis fails, skip this check
            pass
            _ = None  # noqa: BLE001


def analyze_test_directory(test_dir='tests'):
    """Scan test directory for problematic patterns."""
    analyzer = MockPatternAnalyzer()

    for test_file in Path(test_dir).rglob('test_*.py'):
        analyzer.current_file = str(test_file)
        try:
            with open(test_file) as f:
                tree = ast.parse(f.read())
            analyzer.visit(tree)
        except Exception as e:
            print(f"Error analyzing {test_file}: {e}")

    return analyzer.issues


if __name__ == '__main__':
    issues = analyze_test_directory()

    print(f"\n🔍 Found {len(issues)} potential issues:\n")

    if not issues:
        print("✅ No high-severity test patterns detected")
    else:
        for issue in sorted(issues, key=lambda x: x['severity'], reverse=True):
            emoji = '🔴' if issue['severity'] == 'HIGH' else '🟡'
            print(f"{emoji} {issue['file']}:{issue['line']}")
            print(f"   Type: {issue['type']}")
            print(f"   {issue['message']}\n")
