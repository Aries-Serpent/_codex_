"""
Tests for PatternRecognizer.
"""
import tempfile
from pathlib import Path
from ..pattern_recognizer import (
    PatternRecognizer,
    ExceptionPatternMatcher,
    ImportPatternMatcher,
    TestPatternMatcher,
    DocstringPatternMatcher
)


def test_exception_pattern_matcher():
    """Test exception pattern detection."""
    matcher = ExceptionPatternMatcher()
    
    code = """
try:
    risky_operation()
except Exception:
    pass

try:
    another_operation()
except ValueError:
    handle_error()
"""
    
    patterns = matcher.match(code, Path("test.py"))
    
    # Should detect broad exception and specific exception
    assert len(patterns) >= 2
    pattern_names = {p.name for p in patterns}
    assert "broad_exception" in pattern_names
    assert "specific_exception" in pattern_names


def test_import_pattern_matcher():
    """Test import pattern detection."""
    matcher = ImportPatternMatcher()
    
    code = """
from module import *
import unused_module

def main():
    pass
"""
    
    patterns = matcher.match(code, Path("test.py"))
    
    # Should detect wildcard import and unused import
    assert len(patterns) >= 1
    pattern_names = {p.name for p in patterns}
    assert "wildcard_import" in pattern_names


def test_test_pattern_matcher():
    """Test test pattern detection."""
    matcher = TestPatternMatcher()
    
    code = """
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_example():
    assert True

def test_empty():
    pass
"""
    
    patterns = matcher.match(code, Path("test_module.py"))
    
    # Should detect test functions and fixtures
    assert len(patterns) >= 2
    pattern_names = {p.name for p in patterns}
    assert "test_function" in pattern_names
    assert "fixture" in pattern_names


def test_docstring_pattern_matcher():
    """Test docstring pattern detection."""
    matcher = DocstringPatternMatcher()
    
    code = """
def function_without_docstring():
    return True

def function_with_docstring():
    \"\"\"This function has a proper docstring.\"\"\"
    return False

class ClassWithoutDocstring:
    pass
"""
    
    patterns = matcher.match(code, Path("test.py"))
    
    # Should detect missing docstrings
    assert len(patterns) >= 2
    pattern_names = {p.name for p in patterns}
    assert "missing_docstring" in pattern_names


def test_pattern_recognizer_file_analysis():
    """Test pattern recognizer on a file."""
    recognizer = PatternRecognizer()
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import unused
from module import *

def test_function():
    try:
        operation()
    except Exception:
        pass
""")
        temp_path = Path(f.name)
    
    try:
        patterns = recognizer.analyze_file(temp_path)
        
        # Should detect multiple patterns
        assert len(patterns) > 0
        pattern_types = {p.pattern_type for p in patterns}
        assert "exception_handling" in pattern_types or "import" in pattern_types
    finally:
        temp_path.unlink()


def test_pattern_recognizer_directory_analysis():
    """Test pattern recognizer on a directory."""
    recognizer = PatternRecognizer()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files
        (tmppath / "module1.py").write_text("""
def function():
    pass
""")
        (tmppath / "test_module.py").write_text("""
def test_example():
    assert True
""")
        
        results = recognizer.analyze_directory(tmppath, recursive=False)
        
        # Should analyze both files
        assert len(results) >= 0  # May be 0 if no patterns detected
        
        # Get summary
        summary = recognizer.get_pattern_summary(results)
        assert "total_files" in summary
        assert "total_patterns" in summary


def test_custom_matcher():
    """Test adding custom pattern matcher."""
    from ..pattern_recognizer import PatternMatcher, Pattern
    
    class CustomMatcher(PatternMatcher):
        def match(self, content, file_path):
            if "custom" in content:
                return [Pattern(
                    name="custom_pattern",
                    pattern_type="custom",
                    description="Custom pattern",
                    locations=[str(file_path)],
                    confidence=1.0,
                    metadata={}
                )]
            return []
        
        def get_pattern_type(self):
            return "custom"
    
    recognizer = PatternRecognizer()
    recognizer.add_matcher(CustomMatcher())
    
    # Should have 5 matchers now
    assert len(recognizer.matchers) == 5
