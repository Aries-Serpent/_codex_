"""
Tests for codex.metrics.storage module.

This module contains tests for metric storage with JSON and SQLite backends.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import json


class TestMetricStorage:
    """Tests for MetricStorage class."""

    def test_init_with_defaults(self, tmp_path):
        """Test MetricStorage initialization with default paths."""
        from codex.metrics.storage import MetricStorage
        
        # Override defaults for testing
        json_dir = tmp_path / "json"
        sqlite_path = tmp_path / "test.db"
        
        storage = MetricStorage(
            json_dir=json_dir,
            sqlite_path=sqlite_path
        )
        
        assert storage.json_dir == json_dir
        assert storage.sqlite_path == sqlite_path
        assert storage.enable_json is True
        assert storage.enable_sqlite is True
        assert json_dir.exists()

    def test_init_json_only(self, tmp_path):
        """Test MetricStorage with JSON only."""
        from codex.metrics.storage import MetricStorage
        
        json_dir = tmp_path / "json"
        
        storage = MetricStorage(
            json_dir=json_dir,
            enable_json=True,
            enable_sqlite=False
        )
        
        assert storage.enable_json is True
        assert storage.enable_sqlite is False
        assert json_dir.exists()

    def test_init_sqlite_only(self, tmp_path):
        """Test MetricStorage with SQLite only."""
        from codex.metrics.storage import MetricStorage
        
        sqlite_path = tmp_path / "test.db"
        
        storage = MetricStorage(
            sqlite_path=sqlite_path,
            enable_json=False,
            enable_sqlite=True
        )
        
        assert storage.enable_json is False
        assert storage.enable_sqlite is True
        assert sqlite_path.exists()

    def test_init_creates_directories(self, tmp_path):
        """Test that initialization creates necessary directories."""
        from codex.metrics.storage import MetricStorage
        
        json_dir = tmp_path / "nested" / "json" / "dir"
        sqlite_path = tmp_path / "nested" / "db" / "test.db"
        
        storage = MetricStorage(
            json_dir=json_dir,
            sqlite_path=sqlite_path
        )
        
        assert json_dir.exists()
        assert sqlite_path.parent.exists()

    def test_init_disabled(self, tmp_path):
        """Test MetricStorage with both backends disabled."""
        from codex.metrics.storage import MetricStorage
        
        storage = MetricStorage(
            json_dir=tmp_path / "json",
            sqlite_path=tmp_path / "test.db",
            enable_json=False,
            enable_sqlite=False
        )
        
        assert storage.enable_json is False
        assert storage.enable_sqlite is False
        # Directories should not be created when disabled
        assert not (tmp_path / "json").exists()


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_default_json_dir(self):
        """Test DEFAULT_JSON_DIR constant."""
        from codex.metrics.storage import DEFAULT_JSON_DIR
        
        assert isinstance(DEFAULT_JSON_DIR, Path)
        assert "metrics" in str(DEFAULT_JSON_DIR)

    def test_default_sqlite_path(self):
        """Test DEFAULT_SQLITE_PATH constant."""
        from codex.metrics.storage import DEFAULT_SQLITE_PATH
        
        assert isinstance(DEFAULT_SQLITE_PATH, Path)
        assert DEFAULT_SQLITE_PATH.suffix == ".db"

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.metrics.storage import logger
        
        assert logger is not None
        assert logger.name == "codex.metrics.storage"
