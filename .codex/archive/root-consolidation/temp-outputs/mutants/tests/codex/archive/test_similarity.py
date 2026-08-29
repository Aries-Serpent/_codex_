"""
Tests for codex.archive.similarity module.

This module contains tests for similarity utilities.
"""


class TestTokens:
    """Tests for _tokens function."""

    def test_simple_text(self):
        """Test tokenizing simple text."""
        from codex.archive.similarity import _tokens

        result = _tokens("hello world")

        assert result == ["hello", "world"]

    def test_empty_string(self):
        """Test tokenizing empty string."""
        from codex.archive.similarity import _tokens

        result = _tokens("")

        assert result == [], "Result must not be empty"

    def test_punctuation_split(self):
        """Test punctuation splits tokens."""
        from codex.archive.similarity import _tokens

        result = _tokens("hello,world.test")

        assert result == ["hello", "world", "test"]

    def test_code_like_text(self):
        """Test tokenizing code-like text."""
        from codex.archive.similarity import _tokens

        result = _tokens("def func(x):")

        assert "def" in result, "Result must not be empty"
        assert "func" in result, "Result must not be empty"
        assert "x" in result, "Result must not be empty"


class TestShingles:
    """Tests for _shingles function."""

    def test_basic_shingles(self):
        """Test basic shingle generation."""
        from codex.archive.similarity import _shingles

        tokens = ["a", "b", "c", "d", "e"]
        result = _shingles(tokens, k=3)

        assert len(result) == 3, "Result must not be empty"
        assert "a b c" in result, "Result must not be empty"

    def test_shingles_short_input(self):
        """Test shingles with short input."""
        from codex.archive.similarity import _shingles

        tokens = ["a", "b"]
        result = _shingles(tokens, k=5)

        # Shorter than k, returns single shingle of all tokens
        assert "a b" in result, "Result must not be empty"

    def test_shingles_empty(self):
        """Test shingles with empty input."""
        from codex.archive.similarity import _shingles

        result = _shingles([], k=5)

        assert result == set(), "Result must not be empty"


class TestJaccard:
    """Tests for jaccard function."""

    def test_identical_sets(self):
        """Test jaccard of identical sets."""
        from codex.archive.similarity import jaccard

        a = {"a", "b", "c"}
        b = {"a", "b", "c"}

        result = jaccard(a, b)

        assert result == 1.0, "Result must not be empty"

    def test_disjoint_sets(self):
        """Test jaccard of disjoint sets."""
        from codex.archive.similarity import jaccard

        a = {"a", "b"}
        b = {"c", "d"}

        result = jaccard(a, b)

        assert result == 0.0, "Result must not be empty"

    def test_partial_overlap(self):
        """Test jaccard with partial overlap."""
        from codex.archive.similarity import jaccard

        a = {"a", "b", "c"}
        b = {"b", "c", "d"}

        # Intersection = {b, c} = 2
        # Union = {a, b, c, d} = 4
        # Jaccard = 2/4 = 0.5
        result = jaccard(a, b)

        assert result == 0.5, "Result must not be empty"

    def test_empty_sets(self):
        """Test jaccard with empty sets."""
        from codex.archive.similarity import jaccard

        assert jaccard(set(), set()) == 1.0
        assert jaccard(set(), {"a"}) == 0.0
        assert jaccard({"a"}, set()) == 0.0


class TestPyAstHash:
    """Tests for py_ast_hash function."""

    def test_valid_python(self):
        """Test hashing valid Python code."""
        from codex.archive.similarity import py_ast_hash

        code = "def foo(): pass"
        result = py_ast_hash(code)

        assert result != "", "Result must not be empty"
        assert len(result) == 64, "Result must not be empty"

    def test_invalid_python(self):
        """Test hashing invalid Python code."""
        from codex.archive.similarity import py_ast_hash

        code = "def foo(: invalid"
        result = py_ast_hash(code)

        assert result == "", "Result must not be empty"

    def test_deterministic(self):
        """Test hashing is deterministic."""
        from codex.archive.similarity import py_ast_hash

        code = "x = 1 + 2"

        result1 = py_ast_hash(code)
        result2 = py_ast_hash(code)

        assert result1 == result2, "Result must not be empty"


class TestSimhash64:
    """Tests for simhash64 function."""

    def test_basic_hash(self):
        """Test basic simhash generation."""
        from codex.archive.similarity import simhash64

        tokens = ["hello", "world", "test"]
        result = simhash64(tokens)

        assert isinstance(result, int)
        assert result >= 0, "result must be greater than zero"

    def test_deterministic(self):
        """Test simhash is deterministic."""
        from codex.archive.similarity import simhash64

        tokens = ["a", "b", "c"]

        result1 = simhash64(tokens)
        result2 = simhash64(tokens)

        assert result1 == result2, "Result must not be empty"

    def test_empty_tokens(self):
        """Test simhash with empty tokens."""
        from codex.archive.similarity import simhash64

        result = simhash64([])

        # Empty tokens produces a deterministic result based on algorithm
        assert isinstance(result, int)


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.similarity import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.similarity", "name is not valid"
