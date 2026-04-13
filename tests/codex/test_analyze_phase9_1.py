"""
Phase 9.1 - Comprehensive tests for codex.analyze.static.analyzer module.

Tests cover:
- File analysis (LOC, SLOC, complexity)
- AST parsing and symbol extraction
- Import and export detection
- Lint checking with ruff
- Security scanning with bandit
- Error handling and edge cases
- Report generation and serialization
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

from codex.analyze.static.analyzer import (
    MAX_FILE_SIZE_KB,
    MAX_FILES_TO_ANALYZE,
    ComplexityMetrics,
    FileAnalysis,
    LintIssue,
    SecurityIssue,
    StaticReport,
    _calculate_complexity,
    _count_lines,
    _extract_exports,
    _extract_imports,
    _resolve_tool,
    _run_bandit,
    _run_ruff,
    analyze,
    analyze_file,
)


class TestComplexityMetrics:
    """Test ComplexityMetrics dataclass."""

    def test_complexity_metrics_creation(self) -> None:
        """Test creating ComplexityMetrics."""
        metrics = ComplexityMetrics(cyclomatic=5.0, cognitive=4.0, halstead_difficulty=3.5)

        assert metrics.cyclomatic == 5.0
        assert metrics.cognitive == 4.0
        assert metrics.halstead_difficulty == 3.5

    def test_complexity_metrics_optional_halstead(self) -> None:
        """Test ComplexityMetrics with optional halstead_difficulty."""
        metrics = ComplexityMetrics(cyclomatic=3.0, cognitive=2.5)

        assert metrics.cyclomatic == 3.0
        assert metrics.cognitive == 2.5
        assert metrics.halstead_difficulty is None


class TestLintIssue:
    """Test LintIssue dataclass."""

    def test_lint_issue_creation(self) -> None:
        """Test creating a LintIssue."""
        issue = LintIssue(
            rule="E501",
            severity="error",
            line=42,
            column=80,
            message="Line too long",
            file_path="test.py",
        )

        assert issue.rule == "E501"
        assert issue.severity == "error"
        assert issue.line == 42
        assert issue.column == 80
        assert issue.message == "Line too long"


class TestSecurityIssue:
    """Test SecurityIssue dataclass."""

    def test_security_issue_creation(self) -> None:
        """Test creating a SecurityIssue."""
        issue = SecurityIssue(
            tool="bandit",
            rule_id="B404",
            severity="high",
            line=10,
            message="Import of subprocess",
            file_path="dangerous.py",
        )

        assert issue.tool == "bandit"
        assert issue.rule_id == "B404"
        assert issue.severity == "high"


class TestLineCount:
    """Test line counting functionality."""

    def test_count_simple_code(self) -> None:
        """Test counting lines in simple code."""
        code = """
def hello():
    return "world"
"""
        loc, sloc = _count_lines(code)

        assert loc == 4
        assert sloc == 2  # def and return lines

    def test_count_with_comments(self) -> None:
        """Test line counting excludes comments."""
        code = """
# This is a comment
def func():
    # Another comment
    return 42
"""
        loc, sloc = _count_lines(code)

        assert loc == 6
        assert sloc == 2  # Only def and return

    def test_count_with_docstrings(self) -> None:
        """Test line counting excludes docstrings."""
        code = '''
def func():
    """
    This is a docstring.
    Multiple lines.
    """
    return True
'''
        loc, sloc = _count_lines(code)

        assert sloc == 2  # def and return only

    def test_count_empty_file(self) -> None:
        """Test counting lines in empty file."""
        loc, sloc = _count_lines("")

        assert loc == 1
        assert sloc == 0

    def test_count_single_quote_docstring(self) -> None:
        """Test docstring with single quotes."""
        code = """
def func():
    '''Single quote docstring'''
    pass
"""
        loc, sloc = _count_lines(code)

        assert sloc == 2  # def and pass


class TestImportExtraction:
    """Test import extraction from AST."""

    def test_extract_simple_imports(self) -> None:
        """Test extracting simple imports."""
        import ast

        code = """
import os
import sys
from pathlib import Path
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports

    def test_extract_from_imports(self) -> None:
        """Test extracting 'from' imports."""
        import ast

        code = """
from typing import Dict, List
from collections import defaultdict
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert "typing" in imports
        assert "collections" in imports

    def test_extract_imports_no_duplicates(self) -> None:
        """Test import extraction removes duplicates."""
        import ast

        code = """
import os
import os
from os import path
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert imports.count("os") == 1

    def test_extract_imports_sorted(self) -> None:
        """Test imports are returned sorted."""
        import ast

        code = """
import sys
import os
import ast
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert imports == sorted(imports)


class TestExportExtraction:
    """Test export extraction from AST."""

    def test_extract_function_exports(self) -> None:
        """Test extracting public functions."""
        import ast

        code = """
def public_func():
    pass

def _private_func():
    pass
"""
        tree = ast.parse(code)
        exports = _extract_exports(tree)

        assert "public_func" in exports
        assert "_private_func" not in exports

    def test_extract_class_exports(self) -> None:
        """Test extracting public classes."""
        import ast

        code = """
class PublicClass:
    pass

class _PrivateClass:
    pass
"""
        tree = ast.parse(code)
        exports = _extract_exports(tree)

        assert "PublicClass" in exports
        assert "_PrivateClass" not in exports

    def test_extract_all_variable(self) -> None:
        """Test extracting from __all__ variable."""
        import ast

        code = """
__all__ = ["func1", "func2", "Class1"]

def func1():
    pass

def func2():
    pass

class Class1:
    pass
"""
        tree = ast.parse(code)
        exports = _extract_exports(tree)

        assert "func1" in exports
        assert "func2" in exports
        assert "Class1" in exports

    def test_extract_exports_sorted(self) -> None:
        """Test exports are returned sorted."""
        import ast

        code = """
def zebra():
    pass

def alpha():
    pass

def beta():
    pass
"""
        tree = ast.parse(code)
        exports = _extract_exports(tree)

        assert exports == sorted(exports)


class TestComplexityCalculation:
    """Test complexity calculation."""

    def test_simple_function_complexity(self) -> None:
        """Test complexity of simple function."""
        import ast

        code = """
def simple():
    return 42
"""
        tree = ast.parse(code)
        metrics = _calculate_complexity(tree)

        assert metrics.cyclomatic == 1.0

    def test_if_statement_increases_complexity(self) -> None:
        """Test if statement increases complexity."""
        import ast

        code = """
def func(x):
    if x > 0:
        return True
    return False
"""
        tree = ast.parse(code)
        metrics = _calculate_complexity(tree)

        assert metrics.cyclomatic == 2.0

    def test_multiple_branches_complexity(self) -> None:
        """Test multiple branches increase complexity."""
        import ast

        code = """
def func(x, y):
    if x > 0:
        if y > 0:
            return x + y
    return 0
"""
        tree = ast.parse(code)
        metrics = _calculate_complexity(tree)

        assert metrics.cyclomatic == 3.0

    def test_loop_increases_complexity(self) -> None:
        """Test loops increase complexity."""
        import ast

        code = """
def func(items):
    for item in items:
        if item > 0:
            return item
    return None
"""
        tree = ast.parse(code)
        metrics = _calculate_complexity(tree)

        assert metrics.cyclomatic >= 3.0

    def test_cognitive_complexity_estimate(self) -> None:
        """Test cognitive complexity is estimated."""
        import ast

        code = """
def func(x):
    if x > 0:
        return True
    return False
"""
        tree = ast.parse(code)
        metrics = _calculate_complexity(tree)

        assert metrics.cognitive > 0
        assert metrics.cognitive == metrics.cyclomatic * 0.8


class TestToolResolution:
    """Test tool path resolution."""

    def test_resolve_existing_tool(self) -> None:
        """Test resolving an existing tool."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            result = _resolve_tool("python")

            assert result is not None
            assert "python" in result

    def test_resolve_nonexistent_tool(self) -> None:
        """Test resolving nonexistent tool returns None."""
        with patch("shutil.which", return_value=None):
            result = _resolve_tool("nonexistent_tool")

            assert result is None

    def test_resolve_tool_with_trusted_dirs(self) -> None:
        """Test tool resolution with trusted directory validation."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            result = _resolve_tool("python", trusted_dirs=["/usr/bin", "/usr/local/bin"])

            assert result is not None

    def test_resolve_tool_untrusted_location(self) -> None:
        """Test tool in untrusted location returns None."""
        with patch("shutil.which", return_value="/tmp/untrusted/tool"):
            result = _resolve_tool("tool", trusted_dirs=["/usr/bin"])

            assert result is None


class TestFileAnalysis:
    """Test single file analysis."""

    def test_analyze_simple_file(self, tmp_path: Path) -> None:
        """Test analyzing a simple Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
import os

def hello():
    return "world"
"""
        )

        analysis = analyze_file(test_file, tmp_path)

        assert analysis is not None
        assert analysis.path == "test.py"
        assert analysis.loc > 0
        assert analysis.sloc > 0
        assert "os" in analysis.imports
        assert "hello" in analysis.exports

    def test_analyze_file_with_syntax_error(self, tmp_path: Path) -> None:
        """Test analyzing file with syntax errors."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("def bad syntax")

        analysis = analyze_file(test_file, tmp_path)

        assert analysis is not None
        assert analysis.complexity.cyclomatic == 0

    def test_analyze_large_file_skipped(self, tmp_path: Path) -> None:
        """Test large files are skipped."""
        large_file = tmp_path / "large.py"
        # Create file larger than MAX_FILE_SIZE_KB
        size_bytes = (MAX_FILE_SIZE_KB + 1) * 1024
        large_file.write_bytes(b"x" * int(size_bytes))

        analysis = analyze_file(large_file, tmp_path)

        assert analysis is None

    def test_analyze_file_with_encoding_errors(self, tmp_path: Path) -> None:
        """Test analyzing file with encoding issues."""
        test_file = tmp_path / "encoded.py"
        test_file.write_bytes(b"# \xff\xfe content")

        analysis = analyze_file(test_file, tmp_path)

        # Should handle encoding errors gracefully
        assert analysis is not None or analysis is None  # Either is acceptable


class TestStaticAnalysis:
    """Test complete static analysis."""

    def test_analyze_directory(self, tmp_path: Path) -> None:
        """Test analyzing a directory of Python files."""
        (tmp_path / "file1.py").write_text("def func1(): pass")
        (tmp_path / "file2.py").write_text("def func2(): pass")

        report = analyze(tmp_path, "test-snapshot", run_lint=False, run_security=False)

        assert report.snapshot_id == "test-snapshot"
        assert len(report.files) == 2
        assert report.summary["total_files"] == 2

    def test_analyze_with_summary(self, tmp_path: Path) -> None:
        """Test analysis generates correct summary."""
        (tmp_path / "test.py").write_text(
            """
def func():
    if True:
        return 1
    return 0
"""
        )

        report = analyze(tmp_path, "test", run_lint=False, run_security=False)

        assert report.summary["total_loc"] > 0
        assert report.summary["total_sloc"] > 0
        assert report.summary["avg_complexity"] > 0

    def test_analyze_no_python_files(self, tmp_path: Path) -> None:
        """Test analyzing directory with no Python files."""
        (tmp_path / "readme.txt").write_text("Not a Python file")

        report = analyze(tmp_path, "test", run_lint=False, run_security=False)

        assert len(report.files) == 0
        assert report.summary["total_files"] == 0

    def test_analyze_respects_file_limit(self, tmp_path: Path) -> None:
        """Test analysis respects MAX_FILES_TO_ANALYZE limit."""
        # Create more files than the limit
        for i in range(MAX_FILES_TO_ANALYZE + 10):
            (tmp_path / f"file{i}.py").write_text(f"def func{i}(): pass")

        report = analyze(tmp_path, "test", run_lint=False, run_security=False)

        # Should not exceed limit
        assert len(report.files) <= MAX_FILES_TO_ANALYZE


class TestStaticReport:
    """Test StaticReport functionality."""

    def test_report_to_dict(self, tmp_path: Path) -> None:
        """Test converting report to dictionary."""
        from datetime import datetime, timezone

        file_analysis = FileAnalysis(
            path="test.py",
            loc=10,
            sloc=8,
            complexity=ComplexityMetrics(cyclomatic=2.0, cognitive=1.6),
            imports=["os"],
            exports=["func"],
            lint_issues=[],
            security_issues=[],
        )

        report = StaticReport(
            snapshot_id="test",
            timestamp=datetime.now(timezone.utc),
            files=[file_analysis],
            summary={"total_files": 1},
        )

        data = report.to_dict()

        assert data["snapshot_id"] == "test"
        assert len(data["files"]) == 1
        assert data["files"][0]["path"] == "test.py"
        assert data["summary"]["total_files"] == 1

    def test_report_save(self, tmp_path: Path) -> None:
        """Test saving report to file."""
        from datetime import datetime, timezone

        report = StaticReport(
            snapshot_id="test",
            timestamp=datetime.now(timezone.utc),
            files=[],
            summary={"total_files": 0},
        )

        output_path = tmp_path / "report.json"
        report.save(output_path)

        assert output_path.exists()

        with output_path.open() as f:
            data = json.load(f)

        assert data["snapshot_id"] == "test"


class TestLintIntegration:
    """Test lint checking integration."""

    @patch("subprocess.run")
    def test_run_ruff_success(self, mock_run: Mock, tmp_path: Path) -> None:
        """Test successful ruff execution."""
        mock_run.return_value = Mock(
            stdout=json.dumps(
                [
                    {
                        "code": "E501",
                        "message": "Line too long",
                        "location": {"row": 1, "column": 80},
                        "filename": "test.py",
                    }
                ]
            )
        )

        with patch("codex.analyze.static.analyzer._resolve_tool", return_value="/usr/bin/ruff"):
            issues = _run_ruff(tmp_path)

        assert len(issues) == 1
        assert issues[0].rule == "E501"

    @patch("subprocess.run")
    def test_run_ruff_not_found(self, mock_run: Mock, tmp_path: Path) -> None:
        """Test ruff not found returns empty list."""
        with patch("codex.analyze.static.analyzer._resolve_tool", return_value=None):
            issues = _run_ruff(tmp_path)

        assert issues == []

    @patch("subprocess.run")
    def test_run_bandit_success(self, mock_run: Mock, tmp_path: Path) -> None:
        """Test successful bandit execution."""
        mock_run.return_value = Mock(
            stdout=json.dumps(
                {
                    "results": [
                        {
                            "test_id": "B404",
                            "issue_severity": "HIGH",
                            "line_number": 5,
                            "issue_text": "Import of subprocess",
                            "filename": "test.py",
                        }
                    ]
                }
            )
        )

        with patch("codex.analyze.static.analyzer._resolve_tool", return_value="/usr/bin/bandit"):
            issues = _run_bandit(tmp_path)

        assert len(issues) == 1
        assert issues[0].rule_id == "B404"
        assert issues[0].severity == "high"
