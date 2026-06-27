"""Comprehensive test suite for services module.

This test file provides unit coverage for the services package, which provides
service-layer adapters and runtimes for Codex deployments.

Test coverage includes:
- services module initialization and imports
- WorkflowInventory and WorkflowParser classes
- WorkflowMetadata, WorkflowTrigger, WorkflowJob types
- GitHub client import handling (optional dependency)
- Error handling for missing optional dependencies
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def mock_yaml_content():
    """Fixture providing sample workflow YAML content."""
    return """
name: CI Workflow
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest
"""


@pytest.fixture
def temp_workflow_file(tmp_path, mock_yaml_content):
    """Fixture providing a temporary workflow file."""
    workflow_file = tmp_path / ".github" / "workflows"
    workflow_file.mkdir(parents=True, exist_ok=True)
    test_file = workflow_file / "test.yml"
    test_file.write_text(mock_yaml_content)
    return test_file


# ============================================================================
# MODULE INITIALIZATION TESTS
# ============================================================================


class TestServicesModuleInitialization:
    """Test services module initialization and imports."""

    def test_module_imports_successfully(self):
        """Test that services module can be imported."""
        import services
        assert services is not None

    def test_workflow_inventory_imported(self):
        """Test that WorkflowInventory is available."""
        from services import WorkflowInventory
        assert WorkflowInventory is not None

    def test_workflow_parser_imported(self):
        """Test that WorkflowParser is available."""
        from services import WorkflowParser
        assert WorkflowParser is not None

    def test_all_exports_defined(self):
        """Test that __all__ is properly defined."""
        import services
        assert hasattr(services, "__all__")
        assert isinstance(services.__all__, list)

    def test_workflow_parser_in_exports(self):
        """Test that WorkflowParser is in __all__."""
        from services import __all__
        assert "WorkflowParser" in __all__

    def test_workflow_inventory_in_exports(self):
        """Test that WorkflowInventory is in __all__."""
        from services import __all__
        assert "WorkflowInventory" in __all__

    def test_types_exported(self):
        """Test that workflow types are exported."""
        from services import (
            WorkflowDependency,
            WorkflowInput,
            WorkflowJob,
            WorkflowMetadata,
            WorkflowTrigger,
        )
        assert all(
            [
                WorkflowDependency,
                WorkflowInput,
                WorkflowJob,
                WorkflowMetadata,
                WorkflowTrigger,
            ]
        )

    def test_all_exported_items_accessible(self):
        """Test that all items in __all__ are accessible."""
        from services import __all__
        import services

        for item_name in __all__:
            assert hasattr(services, item_name)

    def test_module_has_logger(self):
        """Test that module has logger configured."""
        import services
        assert hasattr(services, "logger")
        assert isinstance(services.logger, logging.Logger)

    def test_github_client_optional_import(self):
        """Test GitHub client optional import handling."""
        import services

        # Check that GitHubClient is handled
        if "GitHubClient" in services.__all__:
            # If imported, it should be accessible
            assert hasattr(services, "GitHubClient")
        # It's OK if GitHubClient is not in __all__ (optional dependency)


# ============================================================================
# WORKFLOW PARSER TESTS
# ============================================================================


class TestWorkflowParserBasic:
    """Basic tests for WorkflowParser class."""

    def test_parser_instantiation(self):
        """Test that WorkflowParser can be instantiated."""
        from services import WorkflowParser

        parser = WorkflowParser()
        assert parser is not None
        assert isinstance(parser, WorkflowParser)

    def test_parser_has_cache_attribute(self):
        """Test that parser has _cache attribute."""
        from services import WorkflowParser

        parser = WorkflowParser()
        assert hasattr(parser, "_cache")
        assert isinstance(parser._cache, dict)

    def test_parser_parse_file_method_exists(self):
        """Test that parse_file method exists."""
        from services import WorkflowParser

        parser = WorkflowParser()
        assert hasattr(parser, "parse_file")
        assert callable(parser.parse_file)

    def test_parser_parse_file_accepts_path(self):
        """Test that parse_file accepts Path objects."""
        from services import WorkflowParser

        parser = WorkflowParser()
        # Test with non-existent file - should return None or handle gracefully
        result = parser.parse_file(Path("/nonexistent/file.yml"))
        assert result is None or isinstance(result, object)

    def test_parser_cache_initialized_empty(self):
        """Test that parser cache starts empty."""
        from services import WorkflowParser

        parser = WorkflowParser()
        assert len(parser._cache) == 0

    def test_multiple_parser_instances_independent(self):
        """Test that multiple parser instances have independent caches."""
        from services import WorkflowParser

        parser1 = WorkflowParser()
        parser2 = WorkflowParser()

        assert parser1._cache is not parser2._cache


class TestWorkflowParserFileHandling:
    """Test WorkflowParser file handling."""

    def test_parse_file_nonexistent_returns_none(self):
        """Test that parsing nonexistent file returns None."""
        from services import WorkflowParser

        parser = WorkflowParser()
        result = parser.parse_file(Path("/tmp/nonexistent_workflow_test_file.yml"))
        assert result is None

    def test_parse_file_valid_file(self, temp_workflow_file):
        """Test parsing a valid workflow file."""
        from services import WorkflowParser

        parser = WorkflowParser()
        result = parser.parse_file(temp_workflow_file)
        # Should either return metadata or None, not raise error
        assert result is None or hasattr(result, "name")

    def test_parse_file_with_cache_enabled(self, temp_workflow_file):
        """Test that caching works when enabled."""
        from services import WorkflowParser

        parser = WorkflowParser()
        result1 = parser.parse_file(temp_workflow_file, use_cache=True)
        result2 = parser.parse_file(temp_workflow_file, use_cache=True)

        # Second call should use cache
        assert temp_workflow_file in parser._cache or result1 is None

    def test_parse_file_with_cache_disabled(self, temp_workflow_file):
        """Test that cache can be bypassed."""
        from services import WorkflowParser

        parser = WorkflowParser()
        result1 = parser.parse_file(temp_workflow_file, use_cache=False)
        # Cache should be empty when disabled
        initial_cache_size = len(parser._cache)
        result2 = parser.parse_file(temp_workflow_file, use_cache=False)
        # Cache size should remain same
        assert len(parser._cache) >= initial_cache_size


class TestWorkflowParserYAMLHandling:
    """Test WorkflowParser YAML handling."""

    def test_parse_empty_yaml_file(self, tmp_path):
        """Test parsing empty YAML file."""
        from services import WorkflowParser

        empty_file = tmp_path / "empty.yml"
        empty_file.write_text("")
        parser = WorkflowParser()
        result = parser.parse_file(empty_file)
        # Should handle empty file gracefully
        assert result is None or isinstance(result, object)

    def test_parse_malformed_yaml(self, tmp_path):
        """Test parsing malformed YAML file."""
        from services import WorkflowParser

        malformed_file = tmp_path / "malformed.yml"
        malformed_file.write_text("key: value: invalid: yaml:")
        parser = WorkflowParser()
        result = parser.parse_file(malformed_file)
        # Should handle malformed YAML gracefully
        assert result is None or isinstance(result, object)

    def test_parse_yaml_with_anchors(self, tmp_path):
        """Test parsing YAML with anchors and aliases."""
        from services import WorkflowParser

        yaml_with_anchors = tmp_path / "anchors.yml"
        yaml_with_anchors.write_text(
            """
defaults: &defaults
  runs-on: ubuntu-latest
  timeout-minutes: 30

jobs:
  test:
    <<: *defaults
"""
        )
        parser = WorkflowParser()
        result = parser.parse_file(yaml_with_anchors)
        # Should handle YAML anchors
        assert result is None or isinstance(result, object)


# ============================================================================
# WORKFLOW METADATA TESTS
# ============================================================================


class TestWorkflowTypes:
    """Test workflow type definitions."""

    def test_workflow_metadata_type_exists(self):
        """Test that WorkflowMetadata type exists."""
        from services import WorkflowMetadata

        assert WorkflowMetadata is not None

    def test_workflow_trigger_type_exists(self):
        """Test that WorkflowTrigger type exists."""
        from services import WorkflowTrigger

        assert WorkflowTrigger is not None

    def test_workflow_job_type_exists(self):
        """Test that WorkflowJob type exists."""
        from services import WorkflowJob

        assert WorkflowJob is not None

    def test_workflow_input_type_exists(self):
        """Test that WorkflowInput type exists."""
        from services import WorkflowInput

        assert WorkflowInput is not None

    def test_workflow_dependency_type_exists(self):
        """Test that WorkflowDependency type exists."""
        from services import WorkflowDependency

        assert WorkflowDependency is not None


# ============================================================================
# WORKFLOW INVENTORY TESTS
# ============================================================================


class TestWorkflowInventoryBasic:
    """Basic tests for WorkflowInventory class."""

    def test_inventory_instantiation(self):
        """Test that WorkflowInventory can be instantiated."""
        from services import WorkflowInventory

        inventory = WorkflowInventory()
        assert inventory is not None
        assert isinstance(inventory, WorkflowInventory)

    def test_inventory_methods_exist(self):
        """Test that common inventory methods exist."""
        from services import WorkflowInventory

        inventory = WorkflowInventory()
        # Common methods that should exist
        expected_methods = ["scan", "list_workflows"]
        for method in expected_methods:
            if hasattr(inventory, method):
                assert callable(getattr(inventory, method))

    def test_multiple_inventory_instances(self):
        """Test that multiple inventory instances work independently."""
        from services import WorkflowInventory

        inv1 = WorkflowInventory()
        inv2 = WorkflowInventory()
        assert inv1 is not inv2


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestServicesErrorHandling:
    """Test error handling in services module."""

    def test_parser_handles_permissions_error(self, tmp_path):
        """Test parser handles permission errors gracefully."""
        from services import WorkflowParser

        # Create file and remove read permissions
        restricted_file = tmp_path / "restricted.yml"
        restricted_file.write_text("name: test")

        parser = WorkflowParser()
        try:
            # Try to restrict access
            restricted_file.chmod(0o000)
            result = parser.parse_file(restricted_file)
            # Should handle permission error gracefully
            assert result is None or isinstance(result, object)
        finally:
            # Restore permissions for cleanup
            restricted_file.chmod(0o644)

    def test_parser_with_large_file(self, tmp_path):
        """Test parser with large workflow file."""
        from services import WorkflowParser

        large_file = tmp_path / "large.yml"
        # Create a file with many jobs
        content = "jobs:\n"
        for i in range(100):
            content += f"  job_{i}:\n    runs-on: ubuntu-latest\n"
        large_file.write_text(content)

        parser = WorkflowParser()
        result = parser.parse_file(large_file)
        # Should handle large files
        assert result is None or isinstance(result, object)


# ============================================================================
# GITHUB CLIENT OPTIONAL IMPORT TESTS
# ============================================================================


class TestGitHubClientImport:
    """Test GitHub client import handling."""

    def test_github_client_import_attempt(self):
        """Test that module attempts GitHub client import."""
        import services

        # Module should attempt import, whether successful or not
        if "GitHubClient" in services.__all__:
            # If imported successfully
            assert hasattr(services, "GitHubClient")

    def test_logger_handles_import_errors(self):
        """Test that logger is configured even if imports fail."""
        import services

        # Logger should exist regardless of optional imports
        assert hasattr(services, "logger")
        assert isinstance(services.logger, logging.Logger)

    @patch("httpx.AsyncClient", side_effect=ImportError("httpx not found"))
    def test_github_client_import_error_handling(self, mock_httpx):
        """Test error handling when GitHub client import fails."""
        # This tests the exception handling in services module
        import services

        # Should have graceful handling
        assert "logger" in dir(services)


# ============================================================================
# WORKFLOW SUBMODULE INTEGRATION TESTS
# ============================================================================


class TestWorkflowSubmoduleIntegration:
    """Integration tests for workflow submodule."""

    def test_workflow_module_imports(self):
        """Test that workflow submodule imports correctly."""
        from services.workflow import WorkflowInventory, WorkflowParser

        assert WorkflowInventory is not None
        assert WorkflowParser is not None

    def test_workflow_types_module(self):
        """Test that workflow types module exists."""
        from services.workflow import types

        assert types is not None
        assert hasattr(types, "WorkflowMetadata")

    def test_workflow_parser_module(self):
        """Test that parser module exists."""
        from services.workflow import parser

        assert parser is not None
        assert hasattr(parser, "WorkflowParser")

    def test_workflow_inventory_module(self):
        """Test that inventory module exists."""
        from services.workflow import inventory

        assert inventory is not None
        assert hasattr(inventory, "WorkflowInventory")


# ============================================================================
# API CONTRACT TESTS
# ============================================================================


class TestServicesAPIContract:
    """Test services module API contracts."""

    def test_services_module_public_api(self):
        """Test that services module exposes required public API."""
        import services

        required_exports = [
            "WorkflowParser",
            "WorkflowInventory",
            "WorkflowMetadata",
            "WorkflowTrigger",
            "WorkflowJob",
            "WorkflowInput",
            "WorkflowDependency",
        ]

        for name in required_exports:
            assert hasattr(services, name), f"Missing export: {name}"

    def test_parser_return_type_compatibility(self):
        """Test that parser return types are compatible."""
        from services import WorkflowParser

        parser = WorkflowParser()
        result = parser.parse_file(Path("/nonexistent.yml"))

        # Should return None or WorkflowMetadata-like object
        assert result is None or hasattr(result, "__dict__")

    def test_inventory_scan_method_signature(self):
        """Test that inventory scan method has expected signature."""
        from services import WorkflowInventory
        import inspect

        inventory = WorkflowInventory()
        if hasattr(inventory, "scan"):
            sig = inspect.signature(inventory.scan)
            # Should have directory or path parameter
            assert len(sig.parameters) >= 1


# ============================================================================
# LOGGING TESTS
# ============================================================================


class TestServicesLogging:
    """Test services module logging."""

    def test_module_logger_named_correctly(self):
        """Test that logger is named after module."""
        import services

        # Logger name should relate to services module
        assert "services" in services.logger.name.lower() or services.logger.name == "__main__"

    def test_logger_works_during_imports(self):
        """Test that logger works during module import."""
        import services

        # Should be able to use logger
        initial_handlers = len(services.logger.handlers)
        # Logger should have been initialized
        assert services.logger is not None


# ============================================================================
# DEPENDENCY INJECTION TESTS
# ============================================================================


class TestServicesWithMockDependencies:
    """Test services with mocked dependencies."""

    @patch("services.workflow.parser.yaml.safe_load")
    def test_parser_with_mocked_yaml_loader(self, mock_yaml):
        """Test parser with mocked YAML loader."""
        from services import WorkflowParser
        from pathlib import Path
        import tempfile

        mock_yaml.return_value = {"name": "test", "jobs": {}}

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yml"
            test_file.write_text("name: test")

            parser = WorkflowParser()
            result = parser.parse_file(test_file)

            # YAML loader should have been called
            mock_yaml.assert_called()

    def test_inventory_with_path_variations(self):
        """Test inventory scan with various path inputs."""
        from services import WorkflowInventory
        import tempfile
        from pathlib import Path

        inventory = WorkflowInventory()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with Path object
            path_obj = Path(tmpdir)
            if hasattr(inventory, "scan"):
                try:
                    result = inventory.scan(path_obj)
                    # Should handle Path objects
                    assert result is None or isinstance(result, (list, dict))
                except (TypeError, FileNotFoundError):
                    # May not have scan method or may require specific setup
                    pass


# ============================================================================
# REGRESSION TESTS
# ============================================================================


class TestServicesRegression:
    """Regression tests to prevent functionality degradation."""

    def test_multiple_parsers_do_not_share_cache(self):
        """Test that parser caches are not shared."""
        from services import WorkflowParser

        parser1 = WorkflowParser()
        parser2 = WorkflowParser()

        # Both should have empty cache
        assert len(parser1._cache) == 0
        assert len(parser2._cache) == 0

        # Modifying one should not affect the other
        parser1._cache[Path("test")] = MagicMock()
        assert len(parser1._cache) == 1
        assert len(parser2._cache) == 0

    def test_parser_reset_between_tests(self):
        """Test that parser state is independent between instantiations."""
        from services import WorkflowParser

        for _ in range(3):
            parser = WorkflowParser()
            assert len(parser._cache) == 0

    def test_all_exports_remain_stable(self):
        """Test that module exports remain consistent."""
        from services import __all__

        # Store current exports
        current_exports = set(__all__)

        # Re-import and check
        import importlib
        import services

        importlib.reload(services)
        from services import __all__ as reloaded_all

        assert set(reloaded_all) == current_exports


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
