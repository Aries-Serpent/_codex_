"""Tests for AST-based detection."""

import tempfile
from pathlib import Path

from tools.dupinv.ast_detector import ASTDetector
from tools.dupinv.ast_parsers.python_parser import PythonASTParser


def test_function_extraction():
    """Test extracting functions from Python file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def hello(name):
    return f"Hello, {name}"

def goodbye(name):
    return f"Goodbye, {name}"
""")

        parser = PythonASTParser()
        signatures = parser.parse_file(test_file)

        assert len(signatures) == 2, "Signatures must not be empty"
        assert signatures[0].name == "hello", "name is not valid"
        assert signatures[1].name == "goodbye", "name is not valid"
        assert signatures[0].parameters == ["name"], "parameters is not valid"


def test_class_extraction():
    """Test extracting classes and methods."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
class MyClass:
    def method1(self, x):
        return x * 2

    def method2(self, x):
        return x + 1
""")

        parser = PythonASTParser()
        signatures = parser.parse_file(test_file)

        # Parser may return class + methods, filter for methods only
        methods = [s for s in signatures if s.is_method]
        assert len(methods) == 2, "Methods must not be empty"
        assert methods[0].name == "method1", "name is not valid"
        assert methods[0].is_method, "Condition must be true"
        assert methods[0].class_name == "MyClass", "class_name is not valid"


def test_syntax_error_handling():
    """Test gracefully handling syntax errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "bad.py"
        test_file.write_text("def broken(:\n    pass")

        parser = PythonASTParser()
        signatures = parser.parse_file(test_file)

        # Should return empty list, not crash
        assert signatures == [], "signatures is not valid"


def test_ast_hash_consistency():
    """Test that same function produces same hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.py"
        file2 = Path(tmpdir) / "file2.py"

        # Same function
        code = """
def process_data(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
"""
        file1.write_text(code)
        file2.write_text(code)

        parser = PythonASTParser()
        sigs1 = parser.parse_file(file1)
        sigs2 = parser.parse_file(file2)

        assert len(sigs1) == 1, "Sigs1 must not be empty"
        assert len(sigs2) == 1, "Sigs2 must not be empty"
        assert sigs1[0].ast_hash == sigs2[0].ast_hash, "ast_hash is not valid"


def test_ast_hash_difference():
    """Test that different functions produce different hashes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.py"
        file2 = Path(tmpdir) / "file2.py"

        file1.write_text("""
def func1(x):
    return x * 2
""")

        file2.write_text("""
def func1(x):
    return x + 2
""")

        parser = PythonASTParser()
        sigs1 = parser.parse_file(file1)
        sigs2 = parser.parse_file(file2)

        assert sigs1[0].ast_hash != sigs2[0].ast_hash, "ast_hash is not valid"


def test_identical_function_detection():
    """Test finding identical functions across files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create files with duplicate functions
        (tmppath / "file1.py").write_text("""
def calculate(x, y):
    return x + y
""")

        (tmppath / "file2.py").write_text("""
def calculate(x, y):
    return x + y
""")

        detector = ASTDetector(tmppath)
        groups = detector.scan()

        # Should find one duplicate group
        assert len(groups) >= 1, "Groups must not be empty"
        found_duplicate = False
        for group in groups:
            if group.type == "function-ast" and len(group.member_files) == 2:
                found_duplicate = True
                break
        assert found_duplicate, "found_duplicate is not valid"


def test_cross_file_detection():
    """Test finding duplicates across multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create directory structure
        subdir = tmppath / "subdir"
        subdir.mkdir()

        (tmppath / "file1.py").write_text("""
def helper(data):
    return sorted(data)
""")

        (subdir / "file2.py").write_text("""
def helper(data):
    return sorted(data)
""")

        detector = ASTDetector(tmppath)
        groups = detector.scan()

        # Should find duplicate across directories
        found = False
        for group in groups:
            if len(group.member_files) >= 2:
                paths = [m.path for m in group.member_files]
                if any("file1.py" in p for p in paths) and any("file2.py" in p for p in paths):
                    found = True
                    break
        assert found, "found is not valid"


def test_threshold_filtering():
    """Test that similarity threshold is respected."""
    # This is a placeholder test - full implementation would test
    # similarity scoring more thoroughly
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        (tmppath / "file1.py").write_text("""
def func(x):
    return x
""")

        detector = ASTDetector(tmppath, similarity_threshold=0.95)
        groups = detector.scan()

        # Should not crash with high threshold
        assert isinstance(groups, list)
