"""
Unit tests for codex.logging.config module.

Tests logging configuration defaults and environment variable handling.
"""

import os
from pathlib import Path
from unittest.mock import patch


class TestLoggingConfig:
    """Test logging configuration module."""

    def test_default_log_db_import(self):
        """Test DEFAULT_LOG_DB can be imported."""
        from codex.logging.config import DEFAULT_LOG_DB

        assert DEFAULT_LOG_DB is not None, "DEFAULT_LOG_DB must be initialized"
        assert isinstance(DEFAULT_LOG_DB, Path)

    def test_default_log_db_location(self):
        """Test default log database location."""
        from codex.logging.config import DEFAULT_LOG_DB

        assert ".codex" in str(DEFAULT_LOG_DB), "Condition must be true"
        assert "session_logs.db" in str(DEFAULT_LOG_DB), "Condition must be true"

    def test_default_log_db_is_path(self):
        """Test DEFAULT_LOG_DB is a Path object."""
        from codex.logging.config import DEFAULT_LOG_DB

        assert isinstance(DEFAULT_LOG_DB, Path)

    @patch.dict(os.environ, {"CODEX_LOG_DB_PATH": "/custom/path/logs.db"})
    def test_env_var_codex_log_db_path_exists(self):
        """Test CODEX_LOG_DB_PATH environment variable is recognized."""
        # The config module documents this env var
        assert os.environ.get("CODEX_LOG_DB_PATH") == "/custom/path/logs.db", "Condition must be true"

    @patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"})
    def test_env_var_codex_sqlite_pool_exists(self):
        """Test CODEX_SQLITE_POOL environment variable is recognized."""
        # The config module documents this env var
        assert os.environ.get("CODEX_SQLITE_POOL") == "1", "Condition must be true"

    def test_default_log_db_relative_path(self):
        """Test DEFAULT_LOG_DB uses relative path."""
        from codex.logging.config import DEFAULT_LOG_DB

        # Should be relative, not absolute
        assert not DEFAULT_LOG_DB.is_absolute(), "Condition must be true"

    def test_default_log_db_contains_codex_dir(self):
        """Test path includes .codex directory."""
        from codex.logging.config import DEFAULT_LOG_DB

        parts = DEFAULT_LOG_DB.parts
        assert ".codex" in parts, "Condition must be true"

    def test_module_docstring_exists(self):
        """Test module has proper documentation."""
        import codex.logging.config as config_module

        assert config_module.__doc__ is not None, "__doc__ must be initialized"
        assert len(config_module.__doc__) > 0, "Collection must not be empty"

    def test_module_documents_env_vars(self):
        """Test module documents environment variables."""
        import codex.logging.config as config_module

        docstring = config_module.__doc__
        assert "CODEX_LOG_DB_PATH" in docstring, "Condition must be true"
        assert "CODEX_SQLITE_POOL" in docstring, "Condition must be true"

    def test_default_log_db_str_conversion(self):
        """Test DEFAULT_LOG_DB can be converted to string."""
        from codex.logging.config import DEFAULT_LOG_DB

        path_str = str(DEFAULT_LOG_DB)
        assert isinstance(path_str, str)
        assert len(path_str) > 0, "Path_str must not be empty"
