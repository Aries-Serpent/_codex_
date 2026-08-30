"""Tests for repo_map CLI module."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = ["tests.phase_5_coverage_cli.conftest"]

try:
    from codex_ml.cli import repo_map
except ImportError:
    repo_map = None


@pytest.mark.skipif(repo_map is None, reason="repo_map not importable")
class TestRepoMapFunctions:
    """Test repo_map utility functions."""

    def test_module_importable(self) -> None:
        """Test that module imports successfully."""
        assert repo_map is not None, "repo_map must be initialized"

    def test_list_top_level_function_exists(self) -> None:
        """Test that _list_top_level function exists."""
        assert hasattr(repo_map, "_list_top_level")
        assert callable(repo_map._list_top_level), "Condition must be true"

    def test_list_key_files_function_exists(self) -> None:
        """Test that _list_key_files function exists."""
        assert hasattr(repo_map, "_list_key_files")
        assert callable(repo_map._list_key_files), "Condition must be true"


@pytest.mark.skipif(repo_map is None, reason="repo_map not importable")
class TestListTopLevel:
    """Test _list_top_level function."""

    def test_list_top_level_empty_dir(self, tmp_path: Path) -> None:
        """Test listing empty directory."""
        result = repo_map._list_top_level(tmp_path)
        assert isinstance(result, list)
        assert len(result) == 0, "Result must not be empty"

    def test_list_top_level_with_files(self, tmp_path: Path) -> None:
        """Test listing directory with files."""
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "file2.py").write_text("code")

        result = repo_map._list_top_level(tmp_path)
        assert isinstance(result, list)
        assert len(result) >= 2, "Result must not be empty"

    def test_list_top_level_with_dirs(self, tmp_path: Path) -> None:
        """Test listing directory with subdirectories."""
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()

        result = repo_map._list_top_level(tmp_path)
        assert isinstance(result, list)
        # Should have directory entries
        assert any("[dir]" in entry for entry in result), "Result must not be empty"

    def test_list_top_level_skips_hidden(self, tmp_path: Path) -> None:
        """Test that hidden files are skipped."""
        (tmp_path / ".hidden").write_text("hidden")
        (tmp_path / "visible.txt").write_text("visible")

        result = repo_map._list_top_level(tmp_path)
        assert isinstance(result, list)
        # Hidden file should not be listed
        assert not any(".hidden" in entry for entry in result), "Result must not be empty"

    def test_list_top_level_sorted(self, tmp_path: Path) -> None:
        """Test that results are sorted."""
        (tmp_path / "z_file.txt").write_text("")
        (tmp_path / "a_file.txt").write_text("")
        (tmp_path / "m_file.txt").write_text("")

        result = repo_map._list_top_level(tmp_path)
        # Results should be sorted
        assert result == sorted(result), "Result must not be empty"


@pytest.mark.skipif(repo_map is None, reason="repo_map not importable")
class TestListKeyFiles:
    """Test _list_key_files function."""

    def test_list_key_files_empty_dir(self, tmp_path: Path) -> None:
        """Test listing key files in empty directory."""
        result = repo_map._list_key_files(tmp_path)
        assert isinstance(result, list)

    def test_list_key_files_with_readme(self, tmp_path: Path) -> None:
        """Test finding README.md."""
        (tmp_path / "README.md").write_text("# Project")

        result = repo_map._list_key_files(tmp_path)
        assert "README.md" in result, "Result must not be empty"

    def test_list_key_files_with_pyproject(self, tmp_path: Path) -> None:
        """Test finding pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("[build-system]")

        result = repo_map._list_key_files(tmp_path)
        assert "pyproject.toml" in result, "Result must not be empty"

    def test_list_key_files_with_docs_readme(self, tmp_path: Path) -> None:
        """Test finding docs/README_ROOT.md."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "README_ROOT.md").write_text("# Docs")

        result = repo_map._list_key_files(tmp_path)
        assert "docs/README_ROOT.md" in result, "Result must not be empty"

    def test_list_key_files_all_present(self, tmp_path: Path) -> None:
        """Test with all key files present."""
        (tmp_path / "README.md").write_text("")
        (tmp_path / "pyproject.toml").write_text("")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "README_ROOT.md").write_text("")

        result = repo_map._list_key_files(tmp_path)
        assert len(result) == 3, "Result must not be empty"
        assert "README.md" in result, "Result must not be empty"
        assert "pyproject.toml" in result, "Result must not be empty"
        assert "docs/README_ROOT.md" in result, "Result must not be empty"


@pytest.mark.skipif(repo_map is None, reason="repo_map not importable")
class TestRepoMapConstants:
    """Test module constants."""

    def test_repo_root_is_path(self) -> None:
        """Test that REPO_ROOT is a Path object."""
        assert isinstance(repo_map.REPO_ROOT, Path)

    def test_repo_root_exists(self) -> None:
        """Test that REPO_ROOT points to existing directory."""
        assert repo_map.REPO_ROOT.exists(), "Condition must be true"
        assert repo_map.REPO_ROOT.is_dir(), "Condition must be true"


@pytest.mark.skipif(repo_map is None, reason="repo_map not importable")
class TestRepoMapIntegration:
    """Integration tests for repo_map."""

    def test_can_call_list_top_level(self) -> None:
        """Test calling list_top_level on REPO_ROOT."""
        result = repo_map._list_top_level(repo_map.REPO_ROOT)
        assert isinstance(result, list)
        assert len(result) > 0, "Result must not be empty"

    def test_can_call_list_key_files(self) -> None:
        """Test calling list_key_files on REPO_ROOT."""
        result = repo_map._list_key_files(repo_map.REPO_ROOT)
        assert isinstance(result, list)
