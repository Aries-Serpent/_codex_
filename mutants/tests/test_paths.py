"""Comprehensive test suite for paths module."""

import os
import tempfile
from pathlib import Path

from src.codex.paths import (
    ANALYSIS_DB,
    CACHE_DIR,
    CODEX_DIR,
    CONFIG_DIR,
    METRICS_DB,
    PARSED_TREES_CACHE,
    REPORTS_DIR,
    SESSION_LOGS_DB,
    SIMILARITY_CACHE,
    ensure_codex_structure,
    get_analysis_db,
    get_cache_path,
    get_db_path,
    get_metrics_db,
    get_report_path,
    get_session_logs_db,
)


class TestPathConstants:
    """Test suite for path constants."""

    def test_codex_dir_is_path(self):
        """Test that CODEX_DIR is a Path object."""
        assert isinstance(CODEX_DIR, Path)

    def test_codex_dir_value(self):
        """Test CODEX_DIR value."""
        assert CODEX_DIR == Path(".codex"), "CODEX_DIR is not valid"

    def test_session_logs_db_is_path(self):
        """Test that SESSION_LOGS_DB is a Path object."""
        assert isinstance(SESSION_LOGS_DB, Path)

    def test_session_logs_db_value(self):
        """Test SESSION_LOGS_DB value."""
        assert SESSION_LOGS_DB == Path(".codex/session_logs.db"), "SESSION_LOGS_DB is not valid"

    def test_analysis_db_is_path(self):
        """Test that ANALYSIS_DB is a Path object."""
        assert isinstance(ANALYSIS_DB, Path)

    def test_analysis_db_value(self):
        """Test ANALYSIS_DB value."""
        assert ANALYSIS_DB == Path(".codex/analysis.db"), "ANALYSIS_DB is not valid"

    def test_metrics_db_is_path(self):
        """Test that METRICS_DB is a Path object."""
        assert isinstance(METRICS_DB, Path)

    def test_metrics_db_value(self):
        """Test METRICS_DB value."""
        assert METRICS_DB == Path(".codex/metrics.db"), "METRICS_DB is not valid"

    def test_cache_dir_is_path(self):
        """Test that CACHE_DIR is a Path object."""
        assert isinstance(CACHE_DIR, Path)

    def test_cache_dir_value(self):
        """Test CACHE_DIR value."""
        assert CACHE_DIR == Path(".codex/cache"), "CACHE_DIR is not valid"

    def test_reports_dir_is_path(self):
        """Test that REPORTS_DIR is a Path object."""
        assert isinstance(REPORTS_DIR, Path)

    def test_reports_dir_value(self):
        """Test REPORTS_DIR value."""
        assert REPORTS_DIR == Path(".codex/reports"), "REPORTS_DIR is not valid"

    def test_config_dir_is_path(self):
        """Test that CONFIG_DIR is a Path object."""
        assert isinstance(CONFIG_DIR, Path)

    def test_config_dir_value(self):
        """Test CONFIG_DIR value."""
        assert CONFIG_DIR == Path(".codex/config"), "CONFIG_DIR is not valid"

    def test_parsed_trees_cache_is_path(self):
        """Test that PARSED_TREES_CACHE is a Path object."""
        assert isinstance(PARSED_TREES_CACHE, Path)

    def test_parsed_trees_cache_value(self):
        """Test PARSED_TREES_CACHE value."""
        assert PARSED_TREES_CACHE == Path(".codex/cache/parsed_trees"), "PARSED_TREES_CACHE is not valid"

    def test_similarity_cache_is_path(self):
        """Test that SIMILARITY_CACHE is a Path object."""
        assert isinstance(SIMILARITY_CACHE, Path)

    def test_similarity_cache_value(self):
        """Test SIMILARITY_CACHE value."""
        assert SIMILARITY_CACHE == Path(".codex/cache/similarity"), "SIMILARITY_CACHE is not valid"


class TestEnsureCodexStructure:
    """Test suite for ensure_codex_structure function."""

    def test_ensure_codex_structure_creates_codex_dir(self):
        """Test that ensure_codex_structure creates .codex directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_cache_dir(self):
        """Test that ensure_codex_structure creates cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/cache").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_parsed_trees_cache(self):
        """Test that ensure_codex_structure creates parsed_trees cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/cache/parsed_trees").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_similarity_cache(self):
        """Test that ensure_codex_structure creates similarity cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/cache/similarity").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_reports_dir(self):
        """Test that ensure_codex_structure creates reports directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/reports").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_reports_archive(self):
        """Test that ensure_codex_structure creates reports archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/reports/archive").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_config_dir(self):
        """Test that ensure_codex_structure creates config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/config").exists(), "Condition must be true"

    def test_ensure_codex_structure_creates_readme(self):
        """Test that ensure_codex_structure creates README.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/README.md").exists(), "Condition must be true"

    def test_ensure_codex_structure_readme_content(self):
        """Test that README contains expected content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            readme_content = Path(".codex/README.md").read_text()
            assert "Codex Local Data Directory" in readme_content, "Data must not be empty"
            assert "session_logs.db" in readme_content, "Content must not be empty"

    def test_ensure_codex_structure_creates_gitignore(self):
        """Test that ensure_codex_structure creates .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            assert Path(".codex/.gitignore").exists(), "Condition must be true"

    def test_ensure_codex_structure_gitignore_content(self):
        """Test that .gitignore contains expected entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            gitignore_content = Path(".codex/.gitignore").read_text()
            assert "*.db" in gitignore_content, "Content must not be empty"
            assert "cache/" in gitignore_content, "Content must not be empty"

    def test_ensure_codex_structure_idempotent(self):
        """Test that ensure_codex_structure is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()
            first_mtime = Path(".codex/README.md").stat().st_mtime

            ensure_codex_structure()
            second_mtime = Path(".codex/README.md").stat().st_mtime

            # File should not have been rewritten
            assert first_mtime == second_mtime, "first_mtime is not valid"


class TestGetDbPath:
    """Test suite for get_db_path function."""

    def test_get_db_path_default(self):
        """Test get_db_path with default settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_db_path("test_db")
            assert isinstance(path, Path)
            assert "test_db.db" in str(path), "Condition must be true"

    def test_get_db_path_with_env_var(self):
        """Test get_db_path with environment variable."""
        with tempfile.TemporaryDirectory():
            os.environ["TEST_DB_PATH"] = os.path.join(tempfile.gettempdir(), "test.db")
            try:
                path = get_db_path("test_db", "TEST_DB_PATH")
                assert str(path) == os.path.join(tempfile.gettempdir(), "test.db"), "Condition must be true"
            finally:
                del os.environ["TEST_DB_PATH"]

    def test_get_db_path_env_var_priority(self):
        """Test that environment variable takes priority."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            os.environ["TEST_DB_PATH"] = "/custom/path/db.db"
            try:
                path = get_db_path("default", "TEST_DB_PATH")
                assert str(path) == "/custom/path/db.db", "Condition must be true"
            finally:
                del os.environ["TEST_DB_PATH"]

    def test_get_db_path_without_env_var(self):
        """Test get_db_path when environment variable is not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_db_path("mydb", "NONEXISTENT_VAR")
            assert ".codex" in str(path), "Condition must be true"
            assert "mydb.db" in str(path), "Condition must be true"

    def test_get_db_path_creates_structure(self):
        """Test that get_db_path ensures structure is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            get_db_path("test_db")
            assert Path(".codex").exists(), "Condition must be true"

    def test_get_db_path_none_env_var(self):
        """Test get_db_path with None env_var."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_db_path("test_db", None)
            assert ".codex" in str(path), "Condition must be true"


class TestGetCachePath:
    """Test suite for get_cache_path function."""

    def test_get_cache_path_parsed_trees(self):
        """Test get_cache_path for parsed_trees."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_cache_path("parsed_trees")
            assert "parsed_trees" in str(path), "Condition must be true"
            assert ".codex/cache" in str(path), "Condition must be true"

    def test_get_cache_path_similarity(self):
        """Test get_cache_path for similarity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_cache_path("similarity")
            assert "similarity" in str(path), "Condition must be true"
            assert ".codex/cache" in str(path), "Condition must be true"

    def test_get_cache_path_custom_type(self):
        """Test get_cache_path with custom cache type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_cache_path("custom_cache")
            assert "custom_cache" in str(path), "Condition must be true"

    def test_get_cache_path_creates_structure(self):
        """Test that get_cache_path creates structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            get_cache_path("test_cache")
            assert Path(".codex/cache").exists(), "Condition must be true"

    def test_get_cache_path_returns_path(self):
        """Test that get_cache_path returns Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_cache_path("test")
            assert isinstance(path, Path)


class TestGetReportPath:
    """Test suite for get_report_path function."""

    def test_get_report_path_default(self):
        """Test get_report_path with default settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_report_path("report.html")
            assert ".codex/reports" in str(path), "Condition must be true"
            assert "report.html" in str(path), "Condition must be true"

    def test_get_report_path_archived(self):
        """Test get_report_path with archive=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_report_path("report.html", archive=True)
            assert ".codex/reports/archive" in str(path), "Condition must be true"
            assert "report.html" in str(path), "Condition must be true"

    def test_get_report_path_not_archived(self):
        """Test get_report_path with archive=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_report_path("report.html", archive=False)
            assert ".codex/reports" in str(path), "Condition must be true"
            assert "archive" not in str(path) or ".codex/reports/archive" not in str(path), "Condition must be true"

    def test_get_report_path_creates_structure(self):
        """Test that get_report_path creates structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            get_report_path("report.html")
            assert Path(".codex/reports").exists(), "Condition must be true"

    def test_get_report_path_archive_creates_archive_dir(self):
        """Test that archive=True creates archive directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            get_report_path("report.html", archive=True)
            assert Path(".codex/reports/archive").exists(), "Condition must be true"

    def test_get_report_path_returns_path(self):
        """Test that get_report_path returns Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_report_path("report.html")
            assert isinstance(path, Path)


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    def test_get_session_logs_db(self):
        """Test get_session_logs_db function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_session_logs_db()
            assert isinstance(path, Path)
            assert "session_logs.db" in str(path), "Condition must be true"

    def test_get_analysis_db(self):
        """Test get_analysis_db function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_analysis_db()
            assert isinstance(path, Path)
            assert "analysis.db" in str(path), "Condition must be true"

    def test_get_metrics_db(self):
        """Test get_metrics_db function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            path = get_metrics_db()
            assert isinstance(path, Path)
            assert "metrics.db" in str(path), "Condition must be true"

    def test_convenience_functions_create_structure(self):
        """Test that convenience functions create structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            get_session_logs_db()
            assert Path(".codex").exists(), "Condition must be true"


class TestEnvironmentVariableHandling:
    """Test suite for environment variable handling."""

    def test_codex_log_db_path_env(self):
        """Test CODEX_LOG_DB_PATH environment variable."""
        os.environ["CODEX_LOG_DB_PATH"] = os.path.join(tempfile.gettempdir(), "custom_logs.db")
        try:
            path = get_session_logs_db()
            assert str(path) == os.path.join(tempfile.gettempdir(), "custom_logs.db"), "Condition must be true"
        finally:
            del os.environ["CODEX_LOG_DB_PATH"]

    def test_codex_analysis_db_path_env(self):
        """Test CODEX_ANALYSIS_DB_PATH environment variable."""
        os.environ["CODEX_ANALYSIS_DB_PATH"] = os.path.join(tempfile.gettempdir(), "custom_analysis.db")
        try:
            path = get_analysis_db()
            assert str(path) == os.path.join(tempfile.gettempdir(), "custom_analysis.db"), "Condition must be true"
        finally:
            del os.environ["CODEX_ANALYSIS_DB_PATH"]

    def test_codex_metrics_db_path_env(self):
        """Test CODEX_METRICS_DB_PATH environment variable."""
        os.environ["CODEX_METRICS_DB_PATH"] = os.path.join(tempfile.gettempdir(), "custom_metrics.db")
        try:
            path = get_metrics_db()
            assert str(path) == os.path.join(tempfile.gettempdir(), "custom_metrics.db"), "Condition must be true"
        finally:
            del os.environ["CODEX_METRICS_DB_PATH"]


class TestPathsIntegration:
    """Integration tests for paths module."""

    def test_all_paths_consistent(self):
        """Test that all paths are consistent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()

            logs_path = get_session_logs_db()
            analysis_path = get_analysis_db()
            metrics_path = get_metrics_db()

            # All should be in .codex directory
            assert ".codex" in str(logs_path), "Condition must be true"
            assert ".codex" in str(analysis_path), "Condition must be true"
            assert ".codex" in str(metrics_path), "Condition must be true"

    def test_directory_structure_complete(self):
        """Test that complete directory structure is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ensure_codex_structure()

            # Check all expected directories exist
            expected_dirs = [
                ".codex",
                ".codex/cache",
                ".codex/cache/parsed_trees",
                ".codex/cache/similarity",
                ".codex/reports",
                ".codex/reports/archive",
                ".codex/config",
            ]

            for dir_path in expected_dirs:
                assert Path(dir_path).exists(), "Condition must be true"

    def test_path_retrieval_consistency(self):
        """Test that path retrieval is consistent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)

            # Get paths multiple times
            path1 = get_session_logs_db()
            path2 = get_session_logs_db()

            assert path1 == path2, "path1 is not valid"
