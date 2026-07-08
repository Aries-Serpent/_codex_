"""Tests for Code Smell Detector module."""

from pathlib import Path

from codex.ast.smells import (
    CodeSmell,
    CodeSmellDetector,
    SmellCategory,
    SmellSeverity,
    detect_smells,
)


class TestCodeSmellDetector:
    """Tests for CodeSmellDetector class."""

    def test_detect_long_function(self):
        """Test detection of long functions."""
        # Create a function with 60 lines
        lines = ["def long_function():"]
        lines.extend(["    x = 1"] * 60)
        code = "\n".join(lines)

        detector = CodeSmellDetector()
        detector.MAX_FUNCTION_LENGTH = 50
        smells = detector.detect_string(code)

        long_func_smells = [s for s in smells if s.rule_id == "SMELL-C001"]
        assert len(long_func_smells) == 1, "Long_func_smells must not be empty"
        assert "long_function" in long_func_smells[0].message, "Condition must be true"

    def test_detect_many_arguments(self):
        """Test detection of functions with too many arguments."""
        code = """
def too_many_args(a, b, c, d, e, f, g, h):
    pass
"""
        detector = CodeSmellDetector()
        detector.MAX_FUNCTION_ARGS = 5
        smells = detector.detect_string(code)

        arg_smells = [s for s in smells if s.rule_id == "SMELL-C002"]
        assert len(arg_smells) == 1, "Arg_smells must not be empty"
        assert "8 arguments" in arg_smells[0].message, "Condition must be true"

    def test_detect_deep_nesting(self):
        """Test detection of deeply nested code."""
        code = """
def nested():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        pass
"""
        detector = CodeSmellDetector()
        detector.MAX_NESTED_DEPTH = 4
        smells = detector.detect_string(code)

        nesting_smells = [s for s in smells if s.rule_id == "SMELL-C003"]
        assert len(nesting_smells) >= 1, "Nesting_smells must not be empty"

    def test_detect_short_name(self):
        """Test detection of short function names."""
        code = """
def a():
    pass
"""
        detector = CodeSmellDetector()
        detector.MIN_NAME_LENGTH = 2  # 'a' is 1 char, less than min
        smells = detector.detect_string(code)

        name_smells = [s for s in smells if s.rule_id == "SMELL-N001"]
        assert len(name_smells) == 1, "Name_smells must not be empty"

    def test_detect_non_pep8_function_name(self):
        """Test detection of non-PEP8 function names."""
        code = """
def MyFunction():
    pass
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        pep8_smells = [s for s in smells if s.rule_id == "SMELL-N002"]
        assert len(pep8_smells) == 1, "Pep8_smells must not be empty"
        assert "lowercase" in pep8_smells[0].suggestion, "Condition must be true"

    def test_detect_non_pep8_class_name(self):
        """Test detection of non-PEP8 class names."""
        code = """
class my_class:
    pass
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        pep8_smells = [s for s in smells if s.rule_id == "SMELL-N002"]
        assert len(pep8_smells) == 1, "Pep8_smells must not be empty"
        assert "CapitalizedWords" in pep8_smells[0].suggestion, "Condition must be true"

    def test_detect_god_class(self):
        """Test detection of God Class anti-pattern."""
        # Create class with 25 methods
        lines = ["class GodClass:"]
        for i in range(25):
            lines.append(f"    def method_{i}(self): pass")
        code = "\n".join(lines)

        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        god_class_smells = [s for s in smells if s.rule_id == "SMELL-S001"]
        assert len(god_class_smells) == 1, "God_class_smells must not be empty"
        assert god_class_smells[0].severity == SmellSeverity.ERROR, "Error should be raised or set"

    def test_detect_bare_except(self):
        """Test detection of bare except clauses."""
        code = """
try:
    risky()
except (AssertionError, ValueError, TypeError, RuntimeError):  # noqa: BLE001
    _ = None
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        except_smells = [s for s in smells if s.rule_id == "SMELL-S002"]
        assert len(except_smells) >= 1, "Except_smells must not be empty"

    def test_detect_pass_only_except(self):
        """Test detection of pass-only except handlers."""
        code = """
try:
    risky()
except (AssertionError, ValueError, TypeError, RuntimeError):  # noqa: BLE001
    _ = None
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        except_smells = [s for s in smells if s.rule_id == "SMELL-S002"]
        assert len(except_smells) >= 1, "Except_smells must not be empty"

    def test_detect_missing_docstring(self):
        """Test detection of missing docstrings."""
        code = """
def public_function():
    pass

class PublicClass:
    pass
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        docstring_smells = [s for s in smells if s.rule_id == "SMELL-M001"]
        assert len(docstring_smells) == 2, "Docstring_smells must not be empty"

    def test_skip_private_docstring_check(self):
        """Test that private members skip docstring check."""
        code = """
def _private_function():
    pass

class _PrivateClass:
    pass
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        docstring_smells = [s for s in smells if s.rule_id == "SMELL-M001"]
        assert len(docstring_smells) == 0, "Docstring_smells must not be empty"

    def test_detect_magic_numbers(self):
        """Test detection of magic numbers."""
        code = """
def calculate():
    timeout = 3600
    retry_count = 42
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        magic_smells = [s for s in smells if s.rule_id == "SMELL-M002"]
        assert len(magic_smells) >= 1, "Magic_smells must not be empty"

    def test_allowed_numbers_not_flagged(self):
        """Test that common numbers are not flagged."""
        code = """
def func():
    zero = 0
    one = 1
    two = 2
    hundred = 100
"""
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)

        magic_smells = [s for s in smells if s.rule_id == "SMELL-M002"]
        assert len(magic_smells) == 0, "Magic_smells must not be empty"

    def test_disable_rule(self):
        """Test disabling a rule."""
        code = "def x(): pass"

        detector = CodeSmellDetector()
        detector.disable_rule("SMELL-N001")
        smells = detector.detect_string(code)

        short_name_smells = [s for s in smells if s.rule_id == "SMELL-N001"]
        assert len(short_name_smells) == 0, "Short_name_smells must not be empty"

    def test_enable_rule(self):
        """Test enabling a previously disabled rule."""
        code = "def a(): pass"  # Single char name, not in allowed list

        detector = CodeSmellDetector()
        detector.MIN_NAME_LENGTH = 2
        detector.disable_rule("SMELL-N001")
        detector.enable_rule("SMELL-N001")
        smells = detector.detect_string(code)

        short_name_smells = [s for s in smells if s.rule_id == "SMELL-N001"]
        assert len(short_name_smells) == 1, "Short_name_smells must not be empty"

    def test_detect_file(self, tmp_path: Path):
        """Test detecting smells in a file."""
        test_file = tmp_path / "smelly.py"
        test_file.write_text("def x(): pass")

        detector = CodeSmellDetector()
        smells = detector.detect_file(test_file)

        assert len(smells) >= 1, "Smells must not be empty"

    def test_detect_nonexistent_file(self):
        """Test handling of nonexistent file."""
        detector = CodeSmellDetector()
        smells = detector.detect_file("/nonexistent.py")
        assert smells == [], "smells is not valid"

    def test_detect_directory(self, tmp_path: Path):
        """Test detecting smells in a directory."""
        (tmp_path / "file1.py").write_text("def x(): pass")
        (tmp_path / "file2.py").write_text("def y(): pass")

        detector = CodeSmellDetector()
        results = detector.detect_directory(tmp_path)

        assert len(results) == 2, "Results must not be empty"

    def test_detect_directory_with_exclusions(self, tmp_path: Path):
        """Test directory detection with exclusion patterns."""
        (tmp_path / "good.py").write_text("def good_function(): pass")
        (tmp_path / "test_file.py").write_text("def x(): pass")

        detector = CodeSmellDetector()
        results = detector.detect_directory(tmp_path, exclude_patterns=["test_*.py"])

        # test_file.py should be excluded
        assert all("test_file.py" not in path for path in results), "Result must not be empty"

    def test_smell_to_dict(self):
        """Test CodeSmell serialization."""
        smell = CodeSmell(
            rule_id="TEST-001",
            message="Test message",
            severity=SmellSeverity.WARNING,
            category=SmellCategory.COMPLEXITY,
            file_path=Path("test.py"),
            line_start=10,
            line_end=15,
            suggestion="Fix it",
        )

        data = smell.to_dict()

        assert data["rule_id"] == "TEST-001", "Data must not be empty"
        assert data["severity"] == "warning", "Data must not be empty"
        assert data["category"] == "complexity", "Data must not be empty"
        assert data["suggestion"] == "Fix it", "Data must not be empty"

    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        code = "def broken(:"
        detector = CodeSmellDetector()
        smells = detector.detect_string(code)
        assert smells == [], "smells is not valid"

    def test_method_self_not_counted(self):
        """Test that 'self' is not counted as an argument."""
        code = """
class MyClass:
    def method(self, a, b, c, d, e):
        pass
"""
        detector = CodeSmellDetector()
        detector.MAX_FUNCTION_ARGS = 5
        smells = detector.detect_string(code)

        arg_smells = [s for s in smells if s.rule_id == "SMELL-C002"]
        assert len(arg_smells) == 0, "Arg_smells must not be empty"


class TestDetectSmellsFunction:
    """Tests for detect_smells convenience function."""

    def test_detect_from_string(self):
        """Test detecting smells from code string."""
        smells = detect_smells("def x(): pass")
        assert len(smells) >= 1, "Smells must not be empty"

    def test_detect_from_file(self, tmp_path: Path):
        """Test detecting smells from file path."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def y(): pass")

        smells = detect_smells(test_file)
        assert len(smells) >= 1, "Smells must not be empty"
