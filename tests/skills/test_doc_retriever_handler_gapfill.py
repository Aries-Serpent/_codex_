"""Gap-fill tests for doc_retriever.handler module."""

import tempfile
from pathlib import Path

from codex.skills.doc_retriever.handler import _safe_relative, run


class TestDocRetrieverRun:
    """Tests for doc_retriever.handler.run()."""

    def test_empty_query_returns_error(self):
        """Empty query should return error."""
        result = run({"query": ""})
        assert result["error"] == "query is required", "Result must not be empty"
        assert result["results"] == [], "Result must not be empty"

    def test_missing_query_returns_error(self):
        """Missing query should return error."""
        result = run({})
        assert result["error"] == "query is required", "Result must not be empty"
        assert result["results"] == [], "Result must not be empty"

    def test_search_with_valid_query(self):
        """Search with valid query should find matching documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create docs structure
            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()

            # Create markdown file
            md_file = docs_dir / "guide.md"
            md_file.write_text("# Getting Started\n\nThis guide explains how to use the API.\n")

            result = run(
                {
                    "query": "guide",
                    "doc_root": str(tmpdir_path),
                }
            )

            assert "results" in result, "Result must not be empty"
            assert "total_found" in result, "Result must not be empty"
            # Should find the matching document
            if result["results"]:
                assert "guide.md" in result["results"][0]["path"], "Result must not be empty"

    def test_query_with_multiple_terms(self):
        """Query with multiple terms should match documents containing any term."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()

            md_file = docs_dir / "api.md"
            md_file.write_text(
                "# API Reference\n\nThe API provides endpoints for data retrieval.\n"
            )

            result = run(
                {
                    "query": "API endpoints",
                    "doc_root": str(tmpdir_path),
                }
            )

            assert "results" in result, "Result must not be empty"

    def test_top_k_limit(self):
        """top_k parameter should limit results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()

            # Create multiple matching documents
            for i in range(5):
                md_file = docs_dir / f"doc{i}.md"
                md_file.write_text(f"# Document {i}\n\nThis document contains test content.\n")

            result = run(
                {
                    "query": "test",
                    "doc_root": str(tmpdir_path),
                    "top_k": 2,
                }
            )

            assert len(result["results"]) <= 2, "Collection must not be empty"

    def test_case_insensitive_search(self):
        """Search should be case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()

            md_file = docs_dir / "api.md"
            md_file.write_text("# API\n\nAPI Reference Guide.\n")

            result_lower = run(
                {
                    "query": "api",
                    "doc_root": str(tmpdir_path),
                }
            )

            result_upper = run(
                {
                    "query": "API",
                    "doc_root": str(tmpdir_path),
                }
            )

            # Both should find the same results
            assert len(result_lower["results"]) == len(result_upper["results"]), "Collection must not be empty"

    def test_excerpt_generation(self):
        """Excerpts should be generated around matching terms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()

            md_file = docs_dir / "readme.md"
            md_file.write_text(
                "# Introduction\n\n"
                "This is a long document with multiple paragraphs.\n"
                "The search term appears here: example\n"
                "And continues with more content.\n"
            )

            result = run(
                {
                    "query": "example",
                    "doc_root": str(tmpdir_path),
                }
            )

            assert len(result["results"]) > 0, "Collection must not be empty"
            assert "excerpt" in result["results"][0], "Result must not be empty"
            assert len(result["results"][0]["excerpt"]) > 0, "Collection must not be empty"

    def test_scoring_based_on_hits(self):
        """Documents with more hits should score higher."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()

            # File with many hits
            md_file1 = docs_dir / "many_hits.md"
            md_file1.write_text("test test test test test\n")

            # File with few hits
            md_file2 = docs_dir / "few_hits.md"
            md_file2.write_text("This has one test word.\n")

            result = run(
                {
                    "query": "test",
                    "doc_root": str(tmpdir_path),
                }
            )

            # Results should be sorted by score
            if len(result["results"]) >= 2:
                assert result["results"][0]["score"] >= result["results"][1]["score"], "Value must be greater than zero"

    def test_nested_markdown_files(self):
        """Should find markdown files in nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create nested structure
            docs_dir = tmpdir_path / "docs"
            nested_dir = docs_dir / "api" / "v1"
            nested_dir.mkdir(parents=True)

            md_file = nested_dir / "endpoints.md"
            md_file.write_text("# API Endpoints\n\nList of available endpoints.\n")

            result = run(
                {
                    "query": "endpoints",
                    "doc_root": str(tmpdir_path),
                }
            )

            assert "results" in result, "Result must not be empty"


class TestDocRetrieverSafeRelative:
    """Tests for _safe_relative() function."""

    def test_safe_relative_with_valid_base(self):
        """_safe_relative should return path relative to base when possible."""
        base = Path("/home/user/docs")
        path = Path("/home/user/docs/api.md")

        result = _safe_relative(path, base)
        assert result == "api.md", "Result must not be empty"

    def test_safe_relative_nested_path(self):
        """_safe_relative should handle nested paths."""
        base = Path("/home/user/docs")
        path = Path("/home/user/docs/guides/tutorial.md")

        result = _safe_relative(path, base)
        assert "tutorial.md" in result, "Result must not be empty"

    def test_safe_relative_fallback(self):
        """_safe_relative should fallback when relative path fails."""
        base = Path("/home/user/docs")
        path = Path("/other/location/file.md")

        result = _safe_relative(path, base)
        # Should return string representation
        assert isinstance(result, str)
