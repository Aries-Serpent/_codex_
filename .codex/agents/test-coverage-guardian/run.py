#!/usr/bin/env python3
"""
Test Coverage Guardian Agent

Ensures security-critical code has comprehensive test coverage.
Focuses on input validation, authentication, authorization, and cryptography.

Usage:
    python run.py --module <module_name>
    python run.py --function <function_name>
    python run.py --security-critical-only
    python run.py --generate-tests
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


class CriticalityLevel(Enum):
    """Code criticality levels."""
    SECURITY_CRITICAL = "security_critical"  # 100% coverage required
    HIGH = "high"                             # 95% coverage required
    MEDIUM = "medium"                         # 80% coverage required
    LOW = "low"                               # No minimum


@dataclass
class CoverageIssue:
    """Represents a test coverage issue."""
    file_path: str
    function_name: str
    line_number: int
    criticality: CriticalityLevel
    current_coverage: float
    required_coverage: float
    missing_lines: list[int]
    missing_branches: list[tuple[int, int]]
    message: str
    test_template: str


class TestCoverageGuardian:
    """Main test coverage guardian agent."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or self._default_config()
        self.issues: list[CoverageIssue] = []
        
        # Security-critical function patterns
        self.critical_patterns = [
            r'def\s+.*validate.*\(',
            r'def\s+.*sanitize.*\(',
            r'def\s+.*authenticate.*\(',
            r'def\s+.*authorize.*\(',
            r'def\s+.*encrypt.*\(',
            r'def\s+.*decrypt.*\(',
            r'def\s+.*hash.*\(',
            r'def\s+.*sign.*\(',
            r'def\s+.*verify.*\(',
            r'def\s+.*check.*permission.*\(',
        ]
        
        # High-criticality patterns
        self.high_patterns = [
            r'def\s+.*login.*\(',
            r'def\s+.*logout.*\(',
            r'def\s+.*password.*\(',
            r'def\s+.*token.*\(',
            r'def\s+.*session.*\(',
            r'def\s+.*api.*key.*\(',
        ]
    
    def _default_config(self) -> dict[str, Any]:
        """Default configuration."""
        return {
            "enabled": True,
            "coverage_thresholds": {
                "security_critical": 100.0,
                "high": 95.0,
                "medium": 80.0,
                "low": 0.0,
            },
            "generate_tests": True,
            "exclude_patterns": [
                "tests/**",
                "**/__init__.py",
                "**/migrations/**",
            ],
        }
    
    def analyze_file(self, file_path: Path) -> list[CoverageIssue]:
        """Analyze a file for test coverage issues."""
        issues = []
        
        if self._should_exclude(file_path):
            return issues
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return issues
        
        # Parse Python file
        if file_path.suffix == ".py":
            try:
                tree = ast.parse(content, filename=str(file_path))
                issues.extend(self._analyze_python_functions(file_path, tree, content))
            except SyntaxError as e:
                print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        
        return issues
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded."""
        path_str = str(file_path)
        for pattern in self.config.get("exclude_patterns", []):
            if Path(path_str).match(pattern):
                return True
        return False
    
    def _analyze_python_functions(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> list[CoverageIssue]:
        """Analyze Python functions for coverage requirements."""
        issues = []
        lines = content.split("\n")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Determine criticality level
                criticality = self._determine_criticality(node.name, node, content)
                
                if criticality == CriticalityLevel.LOW:
                    continue  # Skip low criticality functions
                
                # Check if function has tests
                has_tests = self._has_tests(file_path, node.name)
                
                if not has_tests:
                    required_coverage = self.config["coverage_thresholds"][criticality.value]
                    
                    issues.append(CoverageIssue(
                        file_path=str(file_path),
                        function_name=node.name,
                        line_number=node.lineno,
                        criticality=criticality,
                        current_coverage=0.0,
                        required_coverage=required_coverage,
                        missing_lines=[],
                        missing_branches=[],
                        message=f"Missing tests for {criticality.value} function '{node.name}'",
                        test_template=self._generate_test_template(
                            node, file_path, content, criticality
                        ),
                    ))
        
        return issues
    
    def _determine_criticality(
        self, func_name: str, node: ast.FunctionDef, content: str
    ) -> CriticalityLevel:
        """Determine criticality level of a function."""
        func_source = ast.get_source_segment(content, node) or ""
        
        # Check for security-critical patterns
        for pattern in self.critical_patterns:
            if re.search(pattern, f"def {func_name}("):
                return CriticalityLevel.SECURITY_CRITICAL
        
        # Check for security-related imports or calls in function body
        security_keywords = [
            "password", "token", "secret", "key", "hash", "encrypt",
            "decrypt", "authenticate", "authorize", "validate", "sanitize",
        ]
        
        if any(keyword in func_name.lower() for keyword in security_keywords):
            return CriticalityLevel.SECURITY_CRITICAL
        
        # Check function body for security operations
        if any(keyword in func_source.lower() for keyword in security_keywords):
            return CriticalityLevel.HIGH
        
        # Check for high-criticality patterns
        for pattern in self.high_patterns:
            if re.search(pattern, f"def {func_name}("):
                return CriticalityLevel.HIGH
        
        # Check for input validation
        if "raise ValueError" in func_source or "raise TypeError" in func_source:
            return CriticalityLevel.HIGH
        
        return CriticalityLevel.MEDIUM
    
    def _has_tests(self, file_path: Path, function_name: str) -> bool:
        """Check if function has corresponding tests."""
        # Find test directory
        test_dirs = [
            ROOT / "tests",
            file_path.parent / "tests",
            file_path.parent.parent / "tests",
        ]
        
        # Look for test files
        possible_test_files = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"test_{function_name}.py",
        ]
        
        for test_dir in test_dirs:
            if not test_dir.exists():
                continue
            
            for test_file in possible_test_files:
                test_path = test_dir / test_file
                if test_path.exists():
                    # Check if test file contains test for this function
                    try:
                        test_content = test_path.read_text()
                        if f"test_{function_name}" in test_content or function_name in test_content:
                            return True
                    except Exception:
                        pass
        
        return False
    
    def _generate_test_template(
        self, node: ast.FunctionDef, file_path: Path, content: str, criticality: CriticalityLevel
    ) -> str:
        """Generate test template for a function."""
        func_name = node.name
        
        # Extract function signature
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]
        
        # Determine module path
        try:
            rel_path = file_path.relative_to(ROOT / "src")
            module_path = str(rel_path.with_suffix("")).replace("/", ".")
        except ValueError:
            module_path = file_path.stem
        
        # Generate test template based on criticality
        if criticality == CriticalityLevel.SECURITY_CRITICAL:
            template = self._generate_security_test_template(func_name, args, module_path)
        elif criticality == CriticalityLevel.HIGH:
            template = self._generate_high_priority_test_template(func_name, args, module_path)
        else:
            template = self._generate_standard_test_template(func_name, args, module_path)
        
        return template
    
    def _generate_security_test_template(
        self, func_name: str, args: list[str], module_path: str
    ) -> str:
        """Generate comprehensive security test template."""
        return f'''"""
Security-critical tests for {func_name}.
Coverage requirement: 100%
"""
from __future__ import annotations

import pytest
from {module_path} import {func_name}


class Test{func_name.title().replace("_", "")}:
    """Comprehensive test suite for {func_name}."""
    
    def test_valid_input(self):
        """Test with valid input."""
        # TODO: Implement test with valid input
        result = {func_name}({", ".join(f"valid_{arg}" for arg in args)})
        assert result is not None
    
    @pytest.mark.parametrize(
        "invalid_input,expected_error",
        [
            ("", ValueError),
            (None, TypeError),
            ("../../../etc/passwd", ValueError),
            ("; rm -rf /", ValueError),
            ("$(whoami)", ValueError),
        ],
    )
    def test_invalid_input_rejected(self, invalid_input, expected_error):
        """Test that invalid/malicious inputs are rejected."""
        with pytest.raises(expected_error):
            {func_name}({", ".join(f"invalid_input" if i == 0 else f"valid_{arg}" for i, arg in enumerate(args))})
    
    def test_boundary_conditions(self):
        """Test boundary conditions."""
        # TODO: Test minimum/maximum values
        pass
    
    def test_empty_input(self):
        """Test with empty input."""
        with pytest.raises((ValueError, TypeError)):
            {func_name}({", ".join("''" if arg != "self" else "self" for arg in args)})
    
    def test_unicode_input(self):
        """Test with unicode characters."""
        # TODO: Test unicode handling
        pass
    
    def test_injection_attempts(self):
        """Test common injection attack vectors."""
        attack_vectors = [
            "'; DROP TABLE users--",  # SQL injection
            "<script>alert('xss')</script>",  # XSS
            "../../../../etc/passwd",  # Path traversal
            "${{7*7}}",  # Template injection
        ]
        for vector in attack_vectors:
            with pytest.raises((ValueError, TypeError)):
                {func_name}({", ".join(f"vector" if i == 0 else f"'safe_value'" for i, arg in enumerate(args))})
    
    def test_rate_limiting(self):
        """Test rate limiting if applicable."""
        # TODO: Implement if function has rate limiting
        pass
    
    def test_concurrent_access(self):
        """Test thread safety if applicable."""
        # TODO: Implement concurrent access tests
        pass
'''
    
    def _generate_high_priority_test_template(
        self, func_name: str, args: list[str], module_path: str
    ) -> str:
        """Generate high-priority test template."""
        return f'''"""
High-priority tests for {func_name}.
Coverage requirement: 95%
"""
from __future__ import annotations

import pytest
from {module_path} import {func_name}


def test_{func_name}_valid():
    """Test with valid input."""
    # TODO: Implement test
    result = {func_name}({", ".join(f"valid_{arg}" for arg in args)})
    assert result is not None


def test_{func_name}_invalid():
    """Test with invalid input."""
    with pytest.raises((ValueError, TypeError)):
        {func_name}({", ".join("None" for arg in args)})


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # TODO: Add test cases
        ("valid_input", True),
        ("invalid_input", False),
    ],
)
def test_{func_name}_parametrized(test_input, expected):
    """Parametrized tests for various inputs."""
    result = {func_name}(test_input)
    assert result == expected
'''
    
    def _generate_standard_test_template(
        self, func_name: str, args: list[str], module_path: str
    ) -> str:
        """Generate standard test template."""
        return f'''"""Tests for {func_name}."""
from __future__ import annotations

from {module_path} import {func_name}


def test_{func_name}():
    """Test {func_name} functionality."""
    # TODO: Implement test
    result = {func_name}({", ".join(f"test_{arg}" for arg in args)})
    assert result is not None
'''
    
    def run_coverage_analysis(self, file_path: Path) -> dict[str, Any]:
        """Run pytest coverage analysis on a file."""
        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "--cov=" + str(file_path),
                    "--cov-report=json",
                    "--cov-report=term-missing",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            
            # Parse coverage.json if it exists
            coverage_file = ROOT / "coverage.json"
            if coverage_file.exists():
                with coverage_file.open() as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error running coverage: {e}", file=sys.stderr)
        
        return {}
    
    def generate_report(self) -> dict[str, Any]:
        """Generate coverage report."""
        issues_by_criticality = {}
        for level in CriticalityLevel:
            issues_by_criticality[level.value] = [
                {
                    "file": issue.file_path,
                    "function": issue.function_name,
                    "line": issue.line_number,
                    "current_coverage": issue.current_coverage,
                    "required_coverage": issue.required_coverage,
                    "message": issue.message,
                }
                for issue in self.issues
                if issue.criticality == level
            ]
        
        return {
            "total_issues": len(self.issues),
            "by_criticality": issues_by_criticality,
            "security_critical_count": len([
                i for i in self.issues 
                if i.criticality == CriticalityLevel.SECURITY_CRITICAL
            ]),
            "high_priority_count": len([
                i for i in self.issues 
                if i.criticality == CriticalityLevel.HIGH
            ]),
        }
    
    def generate_test_files(self, output_dir: Path) -> list[Path]:
        """Generate test files for missing coverage."""
        generated_files = []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for issue in self.issues:
            # Create test file name
            file_path = Path(issue.file_path)
            test_file_name = f"test_{file_path.stem}_generated.py"
            test_file_path = output_dir / test_file_name
            
            # Write test template
            if not test_file_path.exists():
                test_file_path.write_text(issue.test_template)
                generated_files.append(test_file_path)
            else:
                # Append to existing file
                existing = test_file_path.read_text()
                if issue.function_name not in existing:
                    test_file_path.write_text(existing + "\n\n" + issue.test_template)
        
        return generated_files


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Coverage Guardian Agent")
    parser.add_argument("--files", nargs="+", help="Files to analyze")
    parser.add_argument("--all", action="store_true", help="Analyze all Python files")
    parser.add_argument("--security-critical-only", action="store_true",
                       help="Only report security-critical functions")
    parser.add_argument("--generate-tests", action="store_true",
                       help="Generate test templates")
    parser.add_argument("--output-dir", default="tests/generated",
                       help="Output directory for generated tests")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    args = parser.parse_args()
    
    guardian = TestCoverageGuardian()
    
    if args.all:
        files = list(ROOT.glob("src/**/*.py"))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        print("Error: Specify --files or --all", file=sys.stderr)
        return 1
    
    # Analyze files
    for file_path in files:
        if file_path.exists() and file_path.is_file():
            issues = guardian.analyze_file(file_path)
            if args.security_critical_only:
                issues = [
                    i for i in issues 
                    if i.criticality == CriticalityLevel.SECURITY_CRITICAL
                ]
            guardian.issues.extend(issues)
    
    # Generate report
    report = guardian.generate_report()
    
    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        # Text output
        print(f"\n{'='*80}")
        print("Test Coverage Guardian - Analysis Results")
        print(f"{'='*80}\n")
        print(f"Total Issues: {report['total_issues']}")
        print(f"Security Critical: {report['security_critical_count']}")
        print(f"High Priority: {report['high_priority_count']}")
        
        print(f"\n{'='*80}")
        print("Issues by Criticality")
        print(f"{'='*80}\n")
        
        for level in ["security_critical", "high", "medium"]:
            issues = report['by_criticality'].get(level, [])
            if issues:
                print(f"\n{level.upper().replace('_', ' ')}:")
                for issue in issues:
                    print(f"  {issue['file']}:{issue['line']} - {issue['function']}")
                    print(f"    Coverage: {issue['current_coverage']:.1f}% / {issue['required_coverage']:.1f}%")
                    print(f"    {issue['message']}")
                    print()
    
    # Generate test files if requested
    if args.generate_tests:
        output_dir = Path(args.output_dir)
        generated = guardian.generate_test_files(output_dir)
        print(f"\n{'='*80}")
        print(f"Generated {len(generated)} test file(s) in {output_dir}")
        print(f"{'='*80}\n")
        for file_path in generated:
            print(f"  {file_path}")
    
    # Return non-zero if security-critical issues found
    if report['security_critical_count'] > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
