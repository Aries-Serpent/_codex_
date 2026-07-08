"""Tests for AST signature similarity analysis."""

# Import from the script
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "analysis"))

try:
    from ast_signature_similarity import (
        compute_uniqueness,
        extract_ast_signature,
        signature_similarity,
    )
except ImportError:
    pytest.skip("AST signature similarity module not found", allow_module_level=True)


class TestASTSignatureSimilarity:
    """Test AST signature similarity analysis functionality."""

    def test_extract_ast_signature_valid_code(self):
        """Test extracting AST signature from valid Python code."""
        code = """
def hello():
    logger.info("Hello, world!")
    return 42
"""
        sig = extract_ast_signature(code)

        assert sig is not None, "sig must be initialized"
        assert "nodes" in sig, "Condition must be true"
        assert "hash" in sig, "Condition must be true"
        assert sig["nodes"]["FunctionDef"] == 1, "Condition must be true"
        assert sig["nodes"]["Return"] == 1, "Condition must be true"
        assert len(sig["hash"]) == 32, "Collection must not be empty"

    def test_extract_ast_signature_invalid_code(self):
        """Test that invalid code returns None."""
        code = "def invalid syntax here"
        sig = extract_ast_signature(code)

        assert sig is None, "sig is not valid"

    def test_signature_similarity_identical(self):
        """Test similarity of identical signatures."""
        code = "x = 1"
        sig1 = extract_ast_signature(code)
        sig2 = extract_ast_signature(code)

        similarity = signature_similarity(sig1, sig2)
        assert similarity == 1.0, "similarity is not valid"

    def test_signature_similarity_different(self):
        """Test similarity of different signatures."""
        code1 = "x = 1"
        code2 = "def foo(): pass"

        sig1 = extract_ast_signature(code1)
        sig2 = extract_ast_signature(code2)

        similarity = signature_similarity(sig1, sig2)
        assert 0.0 <= similarity < 1.0, "0 is not valid"

    def test_compute_uniqueness_single_file(self):
        """Test uniqueness computation with single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.py"
            path.write_text("def foo(): pass")

            uniqueness = compute_uniqueness([path])
            assert uniqueness == 1.0, "uniqueness is not valid"

    def test_compute_uniqueness_identical_files(self):
        """Test uniqueness computation with identical files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "test1.py"
            path2 = Path(tmpdir) / "test2.py"

            code = "def foo(): return 42"
            path1.write_text(code)
            path2.write_text(code)

            uniqueness = compute_uniqueness([path1, path2])
            # Identical files should have low uniqueness (close to 0)
            assert uniqueness < 0.5, "uniqueness is not valid"

    def test_compute_uniqueness_different_files(self):
        """Test uniqueness computation with different files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "test1.py"
            path2 = Path(tmpdir) / "test2.py"

            path1.write_text("def foo(): return 42")
            path2.write_text("class Bar: pass")

            uniqueness = compute_uniqueness([path1, path2])
            # Different files should have higher uniqueness
            assert uniqueness > 0.3, "uniqueness must be greater than zero"

    def test_extract_ast_signature_empty_code(self):
        """Test extracting signature from empty code."""
        sig = extract_ast_signature("")

        assert sig is not None, "sig must be initialized"
        assert "nodes" in sig, "Condition must be true"
        assert "Module" in sig["nodes"], "Condition must be true"

    def test_compute_uniqueness_min_nodes_filter(self):
        """Test that files with too few nodes are filtered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "small.py"
            path2 = Path(tmpdir) / "large.py"

            path1.write_text("x = 1")  # Very small
            path2.write_text("""
def complex_function(a, b, c):
    if a > b:
        return a + c
    elif b > c:
        return b + c
    else:
        return c
""")

            # With high min_nodes, small file should be filtered
            uniqueness = compute_uniqueness([path1, path2], min_nodes=20)
            assert uniqueness == 1.0, "uniqueness is not valid"
