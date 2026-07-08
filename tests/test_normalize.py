"""Tests for normalized duplicate detection."""

import tempfile
from pathlib import Path

from codex.logging.structured_logger import logger


def test_normalized_detector_ignores_comments():
    """Test that files differing only in comments are detected as duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two Python files with same logic but different comments
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        file1.write_text("""# This is file 1
def hello():
    # Print hello
    logger.info('hello')
""")

        file2.write_text("""# This is file 2
def hello():
    # Say hello to the world
    logger.info('hello')
""")

        # Run normalized detector
        from tools.dupinv.normalize import NormalizedDetector

        detector = NormalizedDetector(root)
        groups = detector.scan()

        # Should find one normalized duplicate
        assert len(groups) == 1, "Groups must not be empty"
        assert len(groups[0].member_files) == 2, "Collection must not be empty"
        assert groups[0].type == "normalized-file", "type is not valid"
        assert "formatting-difference" in groups[0].tags, "Condition must be true"


def test_normalized_detector_ignores_whitespace():
    """Test that files with different indentation are detected as duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two Python files with different indentation
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        file1.write_text("""def hello():
    logger.info('hello')
    logger.info('world')
""")

        file2.write_text("""def hello():
  logger.info('hello')
  logger.info('world')
""")

        # Run normalized detector
        from tools.dupinv.normalize import NormalizedDetector

        detector = NormalizedDetector(root)
        groups = detector.scan()

        # Should find one normalized duplicate
        assert len(groups) == 1, "Groups must not be empty"
        assert len(groups[0].member_files) == 2, "Collection must not be empty"


def test_normalized_detector_javascript_comments():
    """Test that JavaScript comments are removed correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two JS files with different comments
        file1 = root / "file1.js"
        file2 = root / "file2.js"

        file1.write_text("""// This is file 1
function hello() {
    // Print hello
    console.log('hello');
}
""")

        file2.write_text("""/* This is file 2 */
function hello() {
    /* Say hello */
    console.log('hello');
}
""")

        # Run normalized detector
        from tools.dupinv.normalize import NormalizedDetector

        detector = NormalizedDetector(root)
        groups = detector.scan()

        # Should find one normalized duplicate
        assert len(groups) == 1, "Groups must not be empty"
        assert len(groups[0].member_files) == 2, "Collection must not be empty"
        assert groups[0].language == "javascript", "language is not valid"


def test_normalized_detector_different_logic_not_matched():
    """Test that files with different logic are not matched."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two files with different logic
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        file1.write_text("""def hello():
    logger.info('hello')
""")

        file2.write_text("""def goodbye():
    logger.info('goodbye')
""")

        # Run normalized detector
        from tools.dupinv.normalize import NormalizedDetector

        detector = NormalizedDetector(root)
        groups = detector.scan()

        # Should find no duplicates
        assert len(groups) == 0, "Groups must not be empty"


def test_normalized_detector_skips_exact_duplicates():
    """Test that exact duplicates are not reported as normalized duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two identical files
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        content = "logger.info('hello')\n"
        file1.write_text(content)
        file2.write_text(content)

        # Run normalized detector
        from tools.dupinv.normalize import NormalizedDetector

        detector = NormalizedDetector(root)
        groups = detector.scan()

        # Should find no duplicates (these are exact, not just normalized)
        assert len(groups) == 0, "Groups must not be empty"


def test_python_normalizer_removes_docstrings():
    """Test that Python docstrings are removed."""
    from tools.dupinv.normalize import PythonNormalizer

    normalizer = PythonNormalizer()

    code_with_docstring = '''def hello():
    """This is a docstring."""
    logger.info('hello')
'''

    code_without_docstring = """def hello():
    logger.info('hello')
"""

    normalized1 = normalizer.normalize(code_with_docstring)
    normalized2 = normalizer.normalize(code_without_docstring)

    # Both should normalize to the same thing
    assert normalized1 == normalized2, "normalized1 is not valid"


def test_javascript_normalizer_removes_multiline_comments():
    """Test that JavaScript multi-line comments are removed."""
    from tools.dupinv.normalize import JavaScriptNormalizer

    normalizer = JavaScriptNormalizer()

    code_with_comment = """function hello() {
    /* This is a
       multi-line comment */
    console.log('hello');
}
"""

    code_without_comment = """function hello() {
    console.log('hello');
}
"""

    normalized1 = normalizer.normalize(code_with_comment)
    normalized2 = normalizer.normalize(code_without_comment)

    # Both should normalize to the same thing
    assert normalized1 == normalized2, "normalized1 is not valid"


def test_normalized_detector_handles_empty_files():
    """Test that empty files are handled gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create empty files
        file1 = root / "empty1.py"
        file2 = root / "empty2.py"

        file1.write_text("")
        file2.write_text("")

        # Run normalized detector
        from tools.dupinv.normalize import NormalizedDetector

        detector = NormalizedDetector(root)
        groups = detector.scan()

        # Empty files should not create groups
        assert len(groups) == 0, "Groups must not be empty"


if __name__ == "__main__":
    # Run tests manually
    import sys

    test_functions = [
        test_normalized_detector_ignores_comments,
        test_normalized_detector_ignores_whitespace,
        test_normalized_detector_javascript_comments,
        test_normalized_detector_different_logic_not_matched,
        test_normalized_detector_skips_exact_duplicates,
        test_python_normalizer_removes_docstrings,
        test_javascript_normalizer_removes_multiline_comments,
        test_normalized_detector_handles_empty_files,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            logger.info(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            logger.info(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            logger.info(f"✗ {test_func.__name__}: {type(e).__name__}: {e}")
            failed += 1

    logger.info(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
