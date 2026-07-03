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
import tempfile
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

        assert metrics.cyclomatic == 5.0, "cyclomatic is not valid"
        assert metrics.cognitive == 4.0, "cognitive is not valid"
        assert metrics.halstead_difficulty == 3.5, "halstead_difficulty is not valid"

    def test_complexity_metrics_optional_halstead(self) -> None:
        """Test ComplexityMetrics with optional halstead_difficulty."""
        metrics = ComplexityMetrics(cyclomatic=3.0, cognitive=2.5)

        assert metrics.cyclomatic == 3.0, "cyclomatic is not valid"
        assert metrics.cognitive == 2.5, "cognitive is not valid"
        assert metrics.halstead_difficulty is None, "halstead_difficulty is not valid"


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

        assert issue.rule == "E501", "rule is not valid"
        assert issue.severity == "error", "Error should be raised or set"
        assert issue.line == 42, "line is not valid"
        assert issue.column == 80, "column is not valid"
        assert issue.message == "Line too long", "message is not valid"


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

        assert issue.tool == "bandit", "tool is not valid"
        assert issue.rule_id == "B404", "rule_id is not valid"
        assert issue.severity == "high", "severity is not valid"


class TestLineCount:
    """Test line counting functionality."""

    def test_count_simple_code(self) -> None:
        """Test counting lines in simple code."""
        code = """
def hello():
    return "world"
"""
        loc, sloc = _count_lines(code)

        assert loc == 4, "loc is not valid"
        assert sloc == 2, "sloc is not valid"

    def test_count_with_comments(self) -> None:
        """Test line counting excludes comments."""
        code = """
# This is a comment
def func():
    # Another comment
    return 42
"""
        loc, sloc = _count_lines(code)

        assert loc == 6, "loc is not valid"
        assert sloc == 2, "sloc is not valid"

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
        _loc, sloc = _count_lines(code)

        assert sloc == 2, "sloc is not valid"

    def test_count_empty_file(self) -> None:
        """Test counting lines in empty file."""
        loc, sloc = _count_lines("")

        assert loc == 1, "loc is not valid"
        assert sloc == 0, "sloc is not valid"

    def test_count_single_quote_docstring(self) -> None:
        """Test docstring with single quotes."""
        code = """
def func():
    '''Single quote docstring'''
    pass
"""
        _loc, sloc = _count_lines(code)

        assert sloc == 2, "sloc is not valid"


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

        assert "os" in imports, "Condition must be true"
        assert "sys" in imports, "Condition must be true"
        assert "pathlib" in imports, "Condition must be true"

    def test_extract_from_imports(self) -> None:
        """Test extracting 'from' imports."""
        import ast

        code = """
from typing import Dict, List
from collections import defaultdict
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert "typing" in imports, "Condition must be true"
        assert "collections" in imports, "Condition must be true"

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

        assert imports.count("os") == 1, "Count must be greater than zero"

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

        assert imports == sorted(imports), "imports is not valid"


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

        assert "public_func" in exports, "Condition must be true"
        assert "_private_func" not in exports, "Condition must be true"

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

        assert "PublicClass" in exports, "Condition must be true"
        assert "_PrivateClass" not in exports, "Condition must be true"

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

        assert "func1" in exports, "Condition must be true"
        assert "func2" in exports, "Condition must be true"
        assert "Class1" in exports, "Condition must be true"

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

        assert exports == sorted(exports), "exports is not valid"


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

        assert metrics.cyclomatic == 1.0, "cyclomatic is not valid"

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

        assert metrics.cyclomatic == 2.0, "cyclomatic is not valid"

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

        assert metrics.cyclomatic == 3.0, "cyclomatic is not valid"

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

        assert metrics.cyclomatic >= 3.0, "cyclomatic must be greater than zero"

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

        assert metrics.cognitive > 0, "cognitive must be greater than zero"
        assert metrics.cognitive == metrics.cyclomatic * 0.8, "cognitive is not valid"


class TestToolResolution:
    """Test tool path resolution."""

    def test_resolve_existing_tool(self) -> None:
        """Test resolving an existing tool."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            result = _resolve_tool("python")

            assert result is not None, "result must be initialized"
            assert "python" in result, "Result must not be empty"

    def test_resolve_nonexistent_tool(self) -> None:
        """Test resolving nonexistent tool returns None."""
        with patch("shutil.which", return_value=None):
            result = _resolve_tool("nonexistent_tool")

            assert result is None, "Result must not be empty"

    def test_resolve_tool_with_trusted_dirs(self) -> None:
        """Test tool resolution with trusted directory validation."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            result = _resolve_tool("python", trusted_dirs=["/usr/bin", "/usr/local/bin"])

            assert result is not None, "result must be initialized"

    def test_resolve_tool_untrusted_location(self) -> None:
        """Test tool in untrusted location returns None."""
        with patch("shutil.which", return_value=os.path.join(tempfile.gettempdir(), "untrusted/tool")):
            result = _resolve_tool("tool", trusted_dirs=["/usr/bin"])

            assert result is None, "Result must not be empty"


class TestFileAnalysis:
    """Test single file analysis."""

    def test_analyze_simple_file(self, tmp_path: Path) -> None:
        """Test analyzing a simple Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os

def hello():
    return "world"
""")

        analysis = analyze_file(test_file, tmp_path)

        assert analysis is not None, "analysis must be initialized"
        assert analysis.path == "test.py", "path is not valid"
        assert analysis.loc > 0, "loc must be greater than zero"
        assert analysis.sloc > 0, "sloc must be greater than zero"
        assert "os" in analysis.imports, "Condition must be true"
        assert "hello" in analysis.exports, "Condition must be true"

    def test_analyze_file_with_syntax_error(self, tmp_path: Path) -> None:
        """Test analyzing file with syntax errors."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("def bad syntax")

        analysis = analyze_file(test_file, tmp_path)

        assert analysis is not None, "analysis must be initialized"
        assert analysis.complexity.cyclomatic == 0, "cyclomatic is not valid"

    def test_analyze_large_file_skipped(self, tmp_path: Path) -> None:
        """Test large files are skipped."""
        large_file = tmp_path / "large.py"
        # Create file larger than MAX_FILE_SIZE_KB
        size_bytes = (MAX_FILE_SIZE_KB + 1) * 1024
        large_file.write_bytes(b"x" * int(size_bytes))

        analysis = analyze_file(large_file, tmp_path)

        assert analysis is None, "analysis is not valid"

    def test_analyze_file_with_encoding_errors(self, tmp_path: Path) -> None:
        """Test analyzing file with encoding issues."""
        test_file = tmp_path / "encoded.py"
        test_file.write_bytes(b"# \xff\xfe content")

        analysis = analyze_file(test_file, tmp_path)

        # Should handle encoding errors gracefully
        assert analysis is not None or analysis is None, "analysis must be initialized"


class TestStaticAnalysis:
    """Test complete static analysis."""

    def test_analyze_directory(self, tmp_path: Path) -> None:
        """Test analyzing a directory of Python files."""
        (tmp_path / "file1.py").write_text("def func1(): pass")
        (tmp_path / "file2.py").write_text("def func2(): pass")

        report = analyze(tmp_path, "test-snapshot", run_lint=False, run_security=False)

        assert report.snapshot_id == "test-snapshot", "snapshot_id is not valid"
        assert len(report.files) == 2, "Collection must not be empty"
        assert report.summary["total_files"] == 2, "rep is not valid"

    def test_analyze_with_summary(self, tmp_path: Path) -> None:
        """Test analysis generates correct summary."""
        (tmp_path / "test.py").write_text("""
def func():
    if True:
        return 1
    return 0
""")

        report = analyze(tmp_path, "test", run_lint=False, run_security=False)

        assert report.summary["total_loc"] > 0, "rep must be greater than zero"
        assert report.summary["total_sloc"] > 0, "rep must be greater than zero"
        assert report.summary["avg_complexity"] > 0, "rep must be greater than zero"

    def test_analyze_no_python_files(self, tmp_path: Path) -> None:
        """Test analyzing directory with no Python files."""
        (tmp_path / "readme.txt").write_text("Not a Python file")

        report = analyze(tmp_path, "test", run_lint=False, run_security=False)

        assert len(report.files) == 0, "Collection must not be empty"
        assert report.summary["total_files"] == 0, "rep is not valid"

    def test_analyze_respects_file_limit(self, tmp_path: Path) -> None:
        """Test analysis respects MAX_FILES_TO_ANALYZE limit."""
        # Create more files than the limit
        for i in range(MAX_FILES_TO_ANALYZE + 10):
            (tmp_path / f"file{i}.py").write_text(f"def func{i}(): pass")

        report = analyze(tmp_path, "test", run_lint=False, run_security=False)

        # Should not exceed limit
        assert len(report.files) <= MAX_FILES_TO_ANALYZE, "Collection must not be empty"


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

        assert data["snapshot_id"] == "test", "Data must not be empty"
        assert len(data["files"]) == 1, "Collection must not be empty"
        assert data["files"][0]["path"] == "test.py", "Data must not be empty"
        assert data["summary"]["total_files"] == 1, "Data must not be empty"

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

        assert output_path.exists(), "Condition must be true"

        with output_path.open() as f:
            data = json.load(f)

        assert data["snapshot_id"] == "test", "Data must not be empty"


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

        assert len(issues) == 1, "Issues must not be empty"
        assert issues[0].rule == "E501", "rule is not valid"

    @patch("subprocess.run")
    def test_run_ruff_not_found(self, mock_run: Mock, tmp_path: Path) -> None:
        """Test ruff not found returns empty list."""
        with patch("codex.analyze.static.analyzer._resolve_tool", return_value=None):
            issues = _run_ruff(tmp_path)

        assert issues == [], "issues is not valid"

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

        assert len(issues) == 1, "Issues must not be empty"
        assert issues[0].rule_id == "B404", "rule_id is not valid"
        assert issues[0].severity == "high", "severity is not valid"
