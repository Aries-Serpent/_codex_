"""
Tests for codex.metrics.storage module.

This module contains tests for metric storage with JSON and SQLite backends.
"""
import pytest
from pathlib import Path
        from codex.metrics.storage import MetricStorage
        from codex.metrics.storage import MetricStorage
        from codex.metrics.storage import MetricStorage
        from codex.metrics.storage import MetricStorage
        from codex.metrics.storage import MetricStorage
        from codex.metrics.storage import DEFAULT_JSON_DIR
        from codex.metrics.storage import DEFAULT_SQLITE_PATH
        from codex.metrics.storage import logger



class TestMetricStorage:
    """Tests for MetricStorage class."""

    def test_init_with_defaults(self, tmp_path):
        """Test MetricStorage initialization with default paths."""

        # Override defaults for testing
        json_dir = tmp_path / "json"
        sqlite_path = tmp_path / "test.db"

        storage = MetricStorage(json_dir=json_dir, sqlite_path=sqlite_path)

        assert storage.json_dir == json_dir, "json_dir is not valid"
        assert storage.sqlite_path == sqlite_path, "sqlite_path is not valid"
        assert storage.enable_json is True, "enable_json is not valid"
        assert storage.enable_sqlite is True, "enable_sqlite is not valid"
        assert json_dir.exists(), "Condition must be true"

    def test_init_json_only(self, tmp_path):
        """Test MetricStorage with JSON only."""

        json_dir = tmp_path / "json"

        storage = MetricStorage(json_dir=json_dir, enable_json=True, enable_sqlite=False)

        assert storage.enable_json is True, "enable_json is not valid"
        assert storage.enable_sqlite is False, "enable_sqlite is not valid"
        assert json_dir.exists(), "Condition must be true"

    def test_init_sqlite_only(self, tmp_path):
        """Test MetricStorage with SQLite only."""

        sqlite_path = tmp_path / "test.db"

        storage = MetricStorage(sqlite_path=sqlite_path, enable_json=False, enable_sqlite=True)

        assert storage.enable_json is False, "enable_json is not valid"
        assert storage.enable_sqlite is True, "enable_sqlite is not valid"
        assert sqlite_path.exists(), "Condition must be true"

    def test_init_creates_directories(self, tmp_path):
        """Test that initialization creates necessary directories."""

        json_dir = tmp_path / "nested" / "json" / "dir"
        sqlite_path = tmp_path / "nested" / "db" / "test.db"

        MetricStorage(json_dir=json_dir, sqlite_path=sqlite_path)

        assert json_dir.exists(), "Condition must be true"
        assert sqlite_path.parent.exists(), "Condition must be true"

    def test_init_disabled(self, tmp_path):
        """Test MetricStorage with both backends disabled."""

        storage = MetricStorage(
            json_dir=tmp_path / "json",
            sqlite_path=tmp_path / "test.db",
            enable_json=False,
            enable_sqlite=False,
        )

        assert storage.enable_json is False, "enable_json is not valid"
        assert storage.enable_sqlite is False, "enable_sqlite is not valid"
        # Directories should not be created when disabled
        assert not (tmp_path / "json").exists(), "Condition must be true"


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_default_json_dir(self):
        """Test DEFAULT_JSON_DIR constant."""

        assert isinstance(DEFAULT_JSON_DIR, Path)
        assert "metrics" in str(DEFAULT_JSON_DIR), "Condition must be true"

    def test_default_sqlite_path(self):
        """Test DEFAULT_SQLITE_PATH constant."""

        assert isinstance(DEFAULT_SQLITE_PATH, Path)
        assert DEFAULT_SQLITE_PATH.suffix == ".db", "suffix is not valid"

    def test_logger_exists(self):
        """Test logger is configured."""

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.metrics.storage", "name is not valid"
