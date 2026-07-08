"""Gap-fill tests for code_search.handler module."""

import tempfile
from pathlib import Path

from codex.skills.code_search.handler import _safe_relative, run


class TestCodeSearchRun:
    """Tests for code_search.handler.run()."""

    def test_empty_query_returns_error(self):
        """Empty query should return error."""
        result = run({"query": ""})
        assert result["error"] == "query is required", "Result must not be empty"
        assert result["matches"] == [], "Result must not be empty"

    def test_missing_query_returns_error(self):
        """Missing query should return error."""
        result = run({})
        assert result["error"] == "query is required", "Result must not be empty"
        assert result["matches"] == [], "Result must not be empty"

    def test_invalid_regex_returns_error(self):
        """Invalid regex pattern should return error."""
        result = run({"query": "(?P<invalid"})  # Invalid regex
        assert "Invalid regex pattern" in result["error"], "Result must not be empty"
        assert result["matches"] == [], "Result must not be empty"

    def test_search_with_valid_pattern(self):
        """Search with valid pattern in temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test file
            test_file = tmpdir_path / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            result = run(
                {
                    "query": "def",
                    "root": str(tmpdir_path),
                    "glob": "*.py",
                }
            )

            assert "matches" in result, "Result must not be empty"
            assert len(result["matches"]) > 0, "Collection must not be empty"
            assert result["matches"][0]["path"] == "test.py", "Result must not be empty"
            assert result["matches"][0]["line"] == 1, "Result must not be empty"
            assert "def" in result["matches"][0]["snippet"], "Result must not be empty"

    def test_case_sensitive_search(self):
        """Case-sensitive search should match only exact case."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test.py"
            test_file.write_text("def hello():\n    return 'WORLD'\n")

            # Case-insensitive (default)
            result_insensitive = run(
                {
                    "query": "world",
                    "root": str(tmpdir_path),
                    "glob": "*.py",
                    "case_sensitive": False,
                }
            )
            assert len(result_insensitive["matches"]) > 0, "Collection must not be empty"

            # Case-sensitive
            result_sensitive = run(
                {
                    "query": "world",
                    "root": str(tmpdir_path),
                    "glob": "*.py",
                    "case_sensitive": True,
                }
            )
            assert len(result_sensitive["matches"]) == 0, "Collection must not be empty"

    def test_top_k_limit(self):
        """top_k parameter should limit results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create multiple test files with "test" in them
            for i in range(5):
                test_file = tmpdir_path / f"test{i}.py"
                test_file.write_text("# test comment\n")

            result = run(
                {
                    "query": "test",
                    "root": str(tmpdir_path),
                    "glob": "*.py",
                    "top_k": 2,
                }
            )

            assert len(result["matches"]) <= 2, "Collection must not be empty"

    def test_pycache_ignored(self):
        """__pycache__ directories should be ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create __pycache__ directory with test file
            cache_dir = tmpdir_path / "__pycache__"
            cache_dir.mkdir()
            cache_file = cache_dir / "test.py"
            cache_file.write_text("# test\n")

            # Also create a regular file
            regular_file = tmpdir_path / "test.py"
            regular_file.write_text("# test\n")

            result = run(
                {
                    "query": "test",
                    "root": str(tmpdir_path),
                    "glob": "**/*.py",
                }
            )

            # Should find the regular file but not cache file
            assert len(result["matches"]) == 1, "Collection must not be empty"
            assert "__pycache__" not in result["matches"][0]["path"], "Result must not be empty"

    def test_context_lines_included(self):
        """Context lines should be included in snippet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test.py"
            content = "line1\nline2\nline3\nline4\nline5\n"
            test_file.write_text(content)

            result = run(
                {
                    "query": "line3",
                    "root": str(tmpdir_path),
                    "glob": "*.py",
                }
            )

            assert len(result["matches"]) > 0, "Collection must not be empty"
            snippet = result["matches"][0]["snippet"]
            # Should include context lines
            assert "line1" in snippet or "line2" in snippet, "Condition must be true"


class TestSafeRelative:
    """Tests for _safe_relative() function."""

    def test_safe_relative_with_valid_base(self):
        """_safe_relative should return path relative to base when possible."""
        base = Path("/home/user/project")
        path = Path("/home/user/project/src/main.py")

        result = _safe_relative(path, base)
        assert result == "src/main.py", "Result must not be empty"

    def test_safe_relative_fallback_to_string(self):
        """_safe_relative should fallback to string when relative path fails."""
        base = Path("/home/user/project")
        path = Path("/other/location/file.py")

        result = _safe_relative(path, base)
        # Should return string representation when relative path fails
        assert isinstance(result, str)

    def test_safe_relative_with_current_dir(self):
        """_safe_relative should handle current directory paths."""
        base = Path.cwd()
        path = base / "test.py"

        result = _safe_relative(path, base)
        assert isinstance(result, str)
        assert "test.py" in result, "Result must not be empty"
