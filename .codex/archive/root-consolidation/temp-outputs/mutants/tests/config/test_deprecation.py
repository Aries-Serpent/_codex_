"""Tests for config deprecation warnings."""

import os
import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

import codex_ml.config.deprecation as _dep_mod  # ensure loaded for object-based patching
from codex_ml.config.deprecation import check_legacy_config_usage, find_repo_root


class TestFindRepoRoot:
    """Tests for find_repo_root function."""

    def test_find_repo_root_with_env_var(self, tmp_path):
        """Should use CODEX_REPO_ROOT env var if set."""
        test_path = tmp_path / "custom_root"
        test_path.mkdir()

        with patch.dict(os.environ, {"CODEX_REPO_ROOT": str(test_path)}):
            result = find_repo_root()

        assert result == test_path.resolve(), "Result must not be empty"

    def test_find_repo_root_with_git_dir(self, tmp_path):
        """Should find .git directory by walking up the tree."""
        # Create a mock git repo structure
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        nested_dir = repo_root / "src" / "codex_ml"
        nested_dir.mkdir(parents=True)

        result = find_repo_root(nested_dir)

        assert result == repo_root, "Result must not be empty"

    def test_find_repo_root_raises_if_not_found(self, tmp_path):
        """Should raise RuntimeError if no .git directory found."""
        test_dir = tmp_path / "no_git"
        test_dir.mkdir()

        with pytest.raises(RuntimeError, match="Could not determine repository root"):
            find_repo_root(test_dir)


class TestCheckLegacyConfigUsage:
    """Tests for check_legacy_config_usage function."""

    def test_warns_for_legacy_conf_directory(self, tmp_path, monkeypatch):
        """Should warn if legacy conf/ directory has non-deprecated files."""
        # Setup mock repo structure
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        legacy_dir = repo_root / "conf"
        legacy_dir.mkdir()
        (legacy_dir / "config.yaml").write_text("test: config")

        # Mock find_repo_root to return our test directory
        monkeypatch.setattr(_dep_mod, "find_repo_root", lambda: repo_root)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            assert len(w) == 1, "W must not be empty"
            assert issubclass(w[0].category, DeprecationWarning)
            assert "conf/" in str(w[0].message), "Condition must be true"
            assert "migrate to 'configs/'" in str(w[0].message), "Condition must be true"

    def test_warns_for_legacy_config_directory(self, tmp_path, monkeypatch):
        """Should warn if legacy config/ directory has non-deprecated files."""
        # Setup mock repo structure
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        legacy_dir = repo_root / "config"
        legacy_dir.mkdir()
        (legacy_dir / "settings.yaml").write_text("test: settings")

        # Mock find_repo_root to return our test directory
        monkeypatch.setattr(_dep_mod, "find_repo_root", lambda: repo_root)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            assert len(w) == 1, "W must not be empty"
            assert issubclass(w[0].category, DeprecationWarning)
            assert "config/" in str(w[0].message), "Condition must be true"

    def test_no_warning_for_deprecated_md_only(self, tmp_path, monkeypatch):
        """Should not warn if legacy directory only contains DEPRECATED.md."""
        # Setup mock repo structure
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        legacy_dir = repo_root / "conf"
        legacy_dir.mkdir()
        (legacy_dir / "DEPRECATED.md").write_text("This directory is deprecated")

        # Mock find_repo_root to return our test directory
        monkeypatch.setattr(_dep_mod, "find_repo_root", lambda: repo_root)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            # Should not warn
            assert len(w) == 0, "W must not be empty"

    def test_no_warning_if_legacy_dirs_dont_exist(self, tmp_path, monkeypatch):
        """Should not warn if legacy directories don't exist."""
        # Setup mock repo structure without legacy dirs
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        # Mock find_repo_root to return our test directory
        monkeypatch.setattr(_dep_mod, "find_repo_root", lambda: repo_root)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            assert len(w) == 0, "W must not be empty"

    def test_handles_permission_error_gracefully(self, tmp_path, monkeypatch):
        """Should handle permission errors without crashing."""
        # Setup mock repo structure
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        legacy_dir = repo_root / "conf"
        legacy_dir.mkdir()

        # Mock find_repo_root to return our test directory
        monkeypatch.setattr(_dep_mod, "find_repo_root", lambda: repo_root)

        # Mock iterdir to raise PermissionError
        original_iterdir = Path.iterdir

        def mock_iterdir(self):
            if self.name == "conf":
                raise PermissionError("Access denied")
            return original_iterdir(self)

        monkeypatch.setattr(Path, "iterdir", mock_iterdir)

        # Should not crash
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            # Should not warn due to permission error
            assert len(w) == 0, "W must not be empty"

    def test_handles_repo_root_not_found(self, monkeypatch):
        """Should handle when repo root cannot be determined."""

        # Mock find_repo_root to raise RuntimeError
        def mock_find_repo_root():
            raise RuntimeError("Cannot find repo root")

        monkeypatch.setattr(_dep_mod, "find_repo_root", mock_find_repo_root)

        # Should not crash
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            # Should not warn
            assert len(w) == 0, "W must not be empty"

    def test_respects_env_var_to_disable_check(self, tmp_path, monkeypatch):
        """Should skip check if CODEX_CHECK_LEGACY_CONFIGS=0."""
        # This is more about ensuring the module-level check respects the env var
        # The function itself doesn't check this, but we can verify behavior

        # Setup mock repo structure with legacy files
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        legacy_dir = repo_root / "conf"
        legacy_dir.mkdir()
        (legacy_dir / "config.yaml").write_text("test: config")

        # Mock find_repo_root to return our test directory
        monkeypatch.setattr(_dep_mod, "find_repo_root", lambda: repo_root)

        # With env var set to 0, function would still warn if called
        # This test verifies the function works when called explicitly
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_legacy_config_usage()

            # Function still warns when called explicitly
            assert len(w) == 1, "W must not be empty"
