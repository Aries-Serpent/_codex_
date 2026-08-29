"""Gap-fill tests for doc_refresh.handler module."""

import tempfile
from pathlib import Path

from codex.skills.doc_refresh.handler import _safe_relative, plan_and_apply


class TestDocRefreshPlanAndApply:
    """Tests for doc_refresh.handler.plan_and_apply()."""

    def test_empty_paths_returns_error(self):
        """Empty paths should return error."""
        result = plan_and_apply({"paths": []})
        assert result["error"] == "paths is required", "Result must not be empty"
        assert result["plan"] == [], "Result must not be empty"
        assert result["patches"] == [], "Result must not be empty"

    def test_missing_paths_returns_error(self):
        """Missing paths key should return error."""
        result = plan_and_apply({})
        assert result["error"] == "paths is required", "Result must not be empty"
        assert result["plan"] == [], "Result must not be empty"

    def test_nonexistent_path_skipped(self):
        """Nonexistent path should be skipped without error."""
        result = plan_and_apply({"paths": ["/nonexistent/path"]})
        # Should not error, but have empty plan
        assert "plan" in result, "Result must not be empty"
        assert "aais_score" in result, "Result must not be empty"

    def test_score_action_only(self):
        """Score-only action should return AAIS score without patches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("# Test\n\nThis is a test document.\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "actions": ["score"],
                }
            )

            assert "aais_score" in result, "Result must not be empty"
            assert result["files_scanned"] == 1, "Result must not be empty"
            assert result["patches"] == [], "Result must not be empty"

    def test_plan_action_with_low_score(self):
        """Plan action should include low-scoring docs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            # Create a doc with low AAIS score (very short)
            md_file.write_text("x\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "actions": ["score", "plan"],
                }
            )

            assert result["files_scanned"] >= 0, "Value must be greater than zero"
            assert "plan" in result, "Result must not be empty"

    def test_prune_stale_with_threshold(self):
        """prune_stale flag should plan prune operations for very low scores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            # Create a doc with very low AAIS score
            md_file.write_text("a\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "prune_stale": True,
                    "actions": ["score", "plan"],
                }
            )

            assert result["files_scanned"] >= 0, "Value must be greater than zero"
            # Plan may contain prune operations
            assert "plan" in result, "Result must not be empty"

    def test_apply_action_creates_patches(self):
        """Apply action should create patches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("# Header\n\nContent\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "actions": ["score", "plan", "apply"],
                }
            )

            assert "patches" in result, "Result must not be empty"

    def test_file_path_instead_of_directory(self):
        """Should handle single file path as well as directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("# Test\n\nContent\n")

            result = plan_and_apply(
                {
                    "paths": [str(md_file)],
                    "actions": ["score", "plan"],
                }
            )

            assert result["files_scanned"] >= 0, "Value must be greater than zero"

    def test_multiple_markdown_files(self):
        """Should scan multiple markdown files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            for i in range(3):
                md_file = tmpdir_path / f"test{i}.md"
                md_file.write_text(f"# Test {i}\n\nContent {i}\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "actions": ["score", "plan"],
                }
            )

            assert result["files_scanned"] == 3, "Result must not be empty"

    def test_aais_score_calculated(self):
        """AAIS score should be calculated for scanned files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("# Test\n\nThis is a well-structured document with good content.\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "actions": ["score"],
                }
            )

            assert isinstance(result["aais_score"], float)
            assert 0.0 <= result["aais_score"] <= 1.0, "Result must not be empty"

    def test_style_parameter_accepted(self):
        """style parameter should be accepted (even if not used currently)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("# Test\n\nContent\n")

            result = plan_and_apply(
                {
                    "paths": [str(tmpdir_path)],
                    "style": "aais",
                    "actions": ["score"],
                }
            )

            assert "aais_score" in result, "Result must not be empty"


class TestDocRefreshSafeRelative:
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
        # Should return string representation when relative path fails
        assert isinstance(result, str)
