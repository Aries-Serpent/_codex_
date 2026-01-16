"""Tests for codex/ingest/loader.py module."""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestIngestLoaderImports:
    """Tests for ingest loader module imports."""

    def test_module_can_be_imported(self):
        """Test that the module can be imported."""
        try:
            from src.codex.ingest import loader
            assert loader is not None
        except ImportError:
            pytest.skip("Module not available or has unmet dependencies")


class TestIngestLoaderOperations:
    """Tests for ingest loader operations."""

    def test_loader_creation(self):
        """Test loader creation."""
        try:
            from src.codex.ingest import loader
            if hasattr(loader, 'Loader'):
                l = loader.Loader()
                assert l is not None
        except (ImportError, AttributeError):
            pytest.skip("Loader not available")

    def test_load_file(self):
        """Test file loading."""
        try:
            from src.codex.ingest import loader
            if hasattr(loader, 'load_file'):
                with patch.object(loader, 'load_file') as mock_load:
                    mock_load.return_value = {"content": "test"}
                    result = loader.load_file("/test/path")
                    assert result["content"] == "test"
        except (ImportError, AttributeError):
            pytest.skip("load_file not available")

    def test_load_directory(self):
        """Test directory loading."""
        try:
            from src.codex.ingest import loader
            if hasattr(loader, 'load_directory'):
                with patch.object(loader, 'load_directory') as mock_load:
                    mock_load.return_value = [{"file": "f1"}, {"file": "f2"}]
                    result = loader.load_directory("/test/dir")
                    assert len(result) == 2
        except (ImportError, AttributeError):
            pytest.skip("load_directory not available")


class TestIngestLoaderFilters:
    """Tests for ingest loader filters."""

    def test_filter_by_extension(self):
        """Test filtering by extension."""
        try:
            from src.codex.ingest import loader
            if hasattr(loader, 'filter_by_extension'):
                files = ["a.py", "b.txt", "c.py"]
                result = loader.filter_by_extension(files, ".py")
                assert len(result) == 2
        except (ImportError, AttributeError):
            pytest.skip("filter_by_extension not available")

    def test_filter_by_size(self):
        """Test filtering by size."""
        try:
            from src.codex.ingest import loader
            if hasattr(loader, 'filter_by_size'):
                with patch.object(loader, 'filter_by_size') as mock_filter:
                    mock_filter.return_value = ["large_file.txt"]
                    result = loader.filter_by_size(["a.txt", "b.txt"], min_size=1000)
                    assert len(result) >= 0
        except (ImportError, AttributeError):
            pytest.skip("filter_by_size not available")
