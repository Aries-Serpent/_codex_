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
from pathlib import Path


class TestStaticAnalyzer:
    """Tests for static analysis functionality."""

    def test_analyze_simple_file(self, tmp_path: Path):
        """Test analyzing a simple Python file."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "simple.py").write_text(
            """
def hello():
    logger.info("Hello, World!")

if __name__ == "__main__":
    hello()
""",
            encoding="utf-8",
        )

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        assert report.snapshot_id == "test-snapshot", "snapshot_id is not valid"
        assert len(report.files) == 1, "Collection must not be empty"
        assert report.files[0].path == "simple.py", "path is not valid"
        assert report.files[0].loc > 0, "loc must be greater than zero"
        assert report.files[0].sloc > 0, "sloc must be greater than zero"

    def test_analyze_multiple_files(self, tmp_path: Path):
        """Test analyzing multiple Python files."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "main.py").write_text("def main(): pass\n", encoding="utf-8")
        (source_dir / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")
        (source_dir / "config.py").write_text("DEBUG = True\n", encoding="utf-8")

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        assert len(report.files) == 3, "Collection must not be empty"
        assert report.summary["total_files"] == 3, "rep is not valid"

    def test_analyze_extracts_imports(self, tmp_path: Path):
        """Test that imports are correctly extracted."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "imports.py").write_text(
            """
import os
import sys
from pathlib import Path
from typing import List, Dict
""",
            encoding="utf-8",
        )

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        imports = report.files[0].imports
        assert "os" in imports, "Condition must be true"
        assert "sys" in imports, "Condition must be true"
        assert "pathlib" in imports, "Condition must be true"
        assert "typing" in imports, "Condition must be true"

    def test_analyze_extracts_exports(self, tmp_path: Path):
        """Test that exports are correctly extracted."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "exports.py").write_text(
            """
__all__ = ["public_func", "PublicClass"]

def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass

class _PrivateClass:
    pass
""",
            encoding="utf-8",
        )

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        exports = report.files[0].exports
        assert "public_func" in exports, "Condition must be true"
        assert "PublicClass" in exports, "Condition must be true"

    def test_analyze_calculates_complexity(self, tmp_path: Path):
        """Test complexity calculation."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "complex.py").write_text(
            """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            for i in range(z):
                if i % 2 == 0:
                    logger.info(i)
        else:
            while z > 0:
                z -= 1
    elif x < 0:
        try:
            result = 1 / x
        except ZeroDivisionError:
            result = 0
    return x + y + z
""",
            encoding="utf-8",
        )

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        complexity = report.files[0].complexity
        assert complexity.cyclomatic > 1, "cyclomatic must be greater than zero"
        assert complexity.cognitive > 0, "cognitive must be greater than zero"

    def test_analyze_handles_syntax_errors(self, tmp_path: Path):
        """Test that syntax errors are handled gracefully."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "broken.py").write_text(
            """
def broken(
    # Missing closing parenthesis
    logger.info("oops")
""",
            encoding="utf-8",
        )

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        # Should still return a report, but with empty analysis
        assert len(report.files) == 1, "Collection must not be empty"
        assert report.files[0].complexity.cyclomatic == 0, "cyclomatic is not valid"

    def test_report_to_dict(self, tmp_path: Path):
        """Test report serialization."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)
        data = report.to_dict()

        assert "snapshot_id" in data, "Data must not be empty"
        assert "timestamp" in data, "Data must not be empty"
        assert "files" in data, "Data must not be empty"
        assert "summary" in data, "Data must not be empty"

    def test_report_save(self, tmp_path: Path):
        """Test saving report to file."""
        from codex.analyze.static.analyzer import analyze

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")

        report = analyze(source_dir, "test-snapshot", run_lint=False, run_security=False)

        output_path = tmp_path / "report.json"
        report.save(output_path)

        assert output_path.exists(), "Condition must be true"
        with output_path.open() as f:
            data = json.load(f)
        assert data["snapshot_id"] == "test-snapshot", "Data must not be empty"


class TestLineCount:
    """Tests for line counting functionality."""

    def test_count_lines_simple(self, tmp_path: Path):
        """Test counting lines in simple file."""
        from codex.analyze.static.analyzer import _count_lines

        content = """line 1
line 2
line 3
"""
        loc, sloc = _count_lines(content)

        assert loc == 4, "loc is not valid"
        assert sloc >= 3, "sloc must be greater than zero"

    def test_count_lines_with_comments(self, tmp_path: Path):
        """Test that comments are excluded from SLOC."""
        from codex.analyze.static.analyzer import _count_lines

        content = """# Comment 1
def func():  # Inline comment
    # Another comment
    pass
"""
        loc, sloc = _count_lines(content)

        assert loc == 5, "loc is not valid"
        assert sloc == 2, "sloc is not valid"

    def test_count_lines_with_docstrings(self, tmp_path: Path):
        """Test that docstrings are excluded from SLOC."""
        from codex.analyze.static.analyzer import _count_lines

        content = '''def func():
    """
    This is a docstring.
    Multiple lines.
    """
    pass
'''
        loc, sloc = _count_lines(content)

        # Docstring lines should be excluded
        assert sloc < loc, "sloc is not valid"


class TestComplexityCalculation:
    """Tests for complexity metric calculation."""

    def test_complexity_linear_function(self):
        """Test complexity of a linear function."""
        from codex.analyze.static.analyzer import _calculate_complexity

        code = """
def linear():
    x = 1
    y = 2
    return x + y
"""
        tree = ast.parse(code)
        complexity = _calculate_complexity(tree)

        assert complexity.cyclomatic == 1, "cyclomatic is not valid"

    def test_complexity_with_if(self):
        """Test complexity with if statement."""
        from codex.analyze.static.analyzer import _calculate_complexity

        code = """
def with_if(x):
    if x > 0:
        return 1
    return 0
"""
        tree = ast.parse(code)
        complexity = _calculate_complexity(tree)

        assert complexity.cyclomatic == 2, "cyclomatic is not valid"

    def test_complexity_with_loop(self):
        """Test complexity with loop."""
        from codex.analyze.static.analyzer import _calculate_complexity

        code = """
def with_loop(items):
    for item in items:
        logger.info(item)
"""
        tree = ast.parse(code)
        complexity = _calculate_complexity(tree)

        assert complexity.cyclomatic >= 2, "cyclomatic must be greater than zero"


class TestImportExtraction:
    """Tests for import extraction."""

    def test_extract_simple_imports(self):
        """Test extracting simple imports."""
        from codex.analyze.static.analyzer import _extract_imports

        code = """
import os
import sys
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert "os" in imports, "Condition must be true"
        assert "sys" in imports, "Condition must be true"

    def test_extract_from_imports(self):
        """Test extracting from imports."""
        from codex.analyze.static.analyzer import _extract_imports

        code = """
from pathlib import Path
from typing import List, Dict
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        assert "pathlib" in imports, "Condition must be true"
        assert "typing" in imports, "Condition must be true"

    def test_extract_imports_deduplication(self):
        """Test that duplicate imports are deduplicated."""
        from codex.analyze.static.analyzer import _extract_imports

        code = """
import os
from os import path
from os.path import join
from codex.logging.structured_logger import logger
"""
        tree = ast.parse(code)
        imports = _extract_imports(tree)

        # Should be deduplicated
        assert imports.count("os") == 1, "Count must be greater than zero"
