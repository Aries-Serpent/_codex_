"""
Comprehensive tests for the Codex Analyze module.

Tests cover:
- Static analysis of Python files
- AST parsing and complexity calculation
- Lint and security issue detection
- Report generation and serialization
"""

import ast
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestStaticAnalyzer:
    """Tests for static analysis functionality."""

    def test_analyze_simple_file(self, tmp_path: Path):
        """Test analyzing a simple Python file."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        (source_dir / "simple.py").write_text("""
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
""", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        assert report.snapshot_id == "test-snapshot"
        assert len(report.files) == 1
        assert report.files[0].path == "simple.py"
        assert report.files[0].loc > 0
        assert report.files[0].sloc > 0

    def test_analyze_multiple_files(self, tmp_path: Path):
        """Test analyzing multiple Python files."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        (source_dir / "main.py").write_text("def main(): pass\n", encoding="utf-8")
        (source_dir / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")
        (source_dir / "config.py").write_text("DEBUG = True\n", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        assert len(report.files) == 3
        assert report.summary["total_files"] == 3

    def test_analyze_extracts_imports(self, tmp_path: Path):
        """Test that imports are correctly extracted."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        (source_dir / "imports.py").write_text("""
import os
import sys
from pathlib import Path
from typing import List, Dict
""", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        imports = report.files[0].imports
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "typing" in imports

    def test_analyze_extracts_exports(self, tmp_path: Path):
        """Test that exports are correctly extracted."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        (source_dir / "exports.py").write_text("""
__all__ = ["public_func", "PublicClass"]

def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass

class _PrivateClass:
    pass
""", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        exports = report.files[0].exports
        assert "public_func" in exports
        assert "PublicClass" in exports

    def test_analyze_calculates_complexity(self, tmp_path: Path):
        """Test complexity calculation."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        (source_dir / "complex.py").write_text("""
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            for i in range(z):
                if i % 2 == 0:
                    print(i)
        else:
            while z > 0:
                z -= 1
    elif x < 0:
        try:
            result = 1 / x
        except ZeroDivisionError:
            result = 0
    return x + y + z
""", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        complexity = report.files[0].complexity
        assert complexity.cyclomatic > 1  # Has multiple branches
        assert complexity.cognitive > 0

    def test_analyze_handles_syntax_errors(self, tmp_path: Path):
        """Test that syntax errors are handled gracefully."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        (source_dir / "broken.py").write_text("""
def broken(
    # Missing closing parenthesis
    print("oops")
""", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        # Should still return a report, but with empty analysis
        assert len(report.files) == 1
        assert report.files[0].complexity.cyclomatic == 0

    def test_report_to_dict(self, tmp_path: Path):
        """Test report serialization."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        data = report.to_dict()
        
        assert "snapshot_id" in data
        assert "timestamp" in data
        assert "files" in data
        assert "summary" in data

    def test_report_save(self, tmp_path: Path):
        """Test saving report to file."""
        from src.codex.analyze.static.analyzer import analyze
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")
        
        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        
        output_path = tmp_path / "report.json"
        report.save(output_path)
        
        assert output_path.exists()
        with output_path.open() as f:
            data = json.load(f)
        assert data["snapshot_id"] == "test-snapshot"


class TestLineCount:
    """Tests for line counting functionality."""

    def test_count_lines_simple(self, tmp_path: Path):
        """Test counting lines in simple file."""
        from src.codex.analyze.static.analyzer import _count_lines
        
        content = """line 1
line 2
line 3
"""
        loc, sloc = _count_lines(content)
        
        assert loc == 4  # Includes trailing newline
        assert sloc >= 3

    def test_count_lines_with_comments(self, tmp_path: Path):
        """Test that comments are excluded from SLOC."""
        from src.codex.analyze.static.analyzer import _count_lines
        
        content = """# Comment 1
def func():  # Inline comment
    # Another comment
    pass
"""
        loc, sloc = _count_lines(content)
        
        assert loc == 5
        assert sloc == 2  # Only 'def' and 'pass' lines

    def test_count_lines_with_docstrings(self, tmp_path: Path):
        """Test that docstrings are excluded from SLOC."""
        from src.codex.analyze.static.analyzer import _count_lines
        
        content = '''def func():
    """
    This is a docstring.
    Multiple lines.
    """
    pass
'''
        loc, sloc = _count_lines(content)
        
        # Docstring lines should be excluded
        assert sloc < loc


class TestComplexityCalculation:
    """Tests for complexity metric calculation."""

    def test_complexity_linear_function(self):
        """Test complexity of a linear function."""
        from src.codex.analyze.static.analyzer import _calculate_complexity
        
        code = """
def linear():
    x = 1
    y = 2
    return x + y
"""
        tree = ast.parse(code)
        complexity = _calculate_complexity(tree)
        
        assert complexity.cyclomatic == 1  # No branches

    def test_complexity_with_if(self):
        """Test complexity with if statement."""
        from src.codex.analyze.static.analyzer import _calculate_complexity
        
        code = """
def with_if(x):
    if x > 0:
        return 1
    return 0
"""
        tree = ast.parse(code)
        complexity = _calculate_complexity(tree)
        
        assert complexity.cyclomatic == 2  # Base + 1 if

    def test_complexity_with_loop(self):
        """Test complexity with loop."""
        from src.codex.analyze.static.analyzer import _calculate_complexity
        
        code = """
def with_loop(items):
    for item in items:
        print(item)
"""
        tree = ast.parse(code)
        complexity = _calculate_complexity(tree)
        
        assert complexity.cyclomatic >= 2


class TestImportExtraction:
    """Tests for import extraction."""

    def test_extract_simple_imports(self):
        """Test extracting simple imports."""
        from src.codex.analyze.static.analyzer import _extract_imports
        
        code = """
import os
import sys
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)
        
        assert "os" in imports
        assert "sys" in imports

    def test_extract_from_imports(self):
        """Test extracting from imports."""
        from src.codex.analyze.static.analyzer import _extract_imports
        
        code = """
from pathlib import Path
from typing import List, Dict
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)
        
        assert "pathlib" in imports
        assert "typing" in imports

    def test_extract_imports_deduplication(self):
        """Test that duplicate imports are deduplicated."""
        from src.codex.analyze.static.analyzer import _extract_imports
        
        code = """
import os
from os import path
from os.path import join
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)
        
        # Should be deduplicated
        assert imports.count("os") == 1
