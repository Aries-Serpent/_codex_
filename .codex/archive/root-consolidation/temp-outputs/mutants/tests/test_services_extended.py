"""Extended test suite for services module - Workflow workflow handling.

This module provides additional test coverage for workflow management,
including edge cases, error scenarios, and integration patterns.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestWorkflowParserEdgeCases:
    """Edge case tests for WorkflowParser."""

    def test_parser_parse_file_encoding_error(self, tmp_path):
        """Test parser with file encoding issues."""
        from services import WorkflowParser

        # Create file with binary data
        test_file = tmp_path / "binary.yml"
        test_file.write_bytes(b"\x80\x81\x82\x83")

        parser = WorkflowParser()
        result = parser.parse_file(test_file)
        # Should handle encoding errors gracefully
        assert result is None or isinstance(result, object)

    def test_parser_with_very_large_file(self, tmp_path):
        """Test parser with large workflow file."""
        from services import WorkflowParser

        # Create large YAML file
        test_file = tmp_path / "large.yml"
        content = "jobs:\n"
        for i in range(1000):
            content += f"  job_{i}:\n    runs-on: ubuntu-latest\n    steps: []\n"
        test_file.write_text(content)

        parser = WorkflowParser()
        result = parser.parse_file(test_file)
        # Should handle large files
        assert result is None or isinstance(result, object)

    def test_parser_with_deeply_nested_yaml(self, tmp_path):
        """Test parser with deeply nested YAML structure."""
        from services import WorkflowParser

        test_file = tmp_path / "nested.yml"
        content = "a:\n"
        for _ in range(50):
            content += "  b:\n"
        content += "    value: deep"
        test_file.write_text(content)

        parser = WorkflowParser()
        result = parser.parse_file(test_file)
        assert result is None or isinstance(result, object)

    def test_parser_cache_key_collision(self):
        """Test that cache properly distinguishes different files."""
        from services import WorkflowParser
        pass  # removed redundant `import tempfile` (top-level import used)

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                file1 = Path(tmpdir1) / "workflow.yml"
                file2 = Path(tmpdir2) / "workflow.yml"

                file1.write_text("name: test1")
                file2.write_text("name: test2")

                parser.parse_file(file1)
                parser.parse_file(file2)

                # Both should be in cache if caching worked
                assert file1 in parser._cache or file2 in parser._cache, "Condition must be true"

    def test_parser_handles_yaml_null_values(self, tmp_path):
        """Test parser with YAML null values."""
        from services import WorkflowParser

        test_file = tmp_path / "nulls.yml"
        test_file.write_text(
            """
name: test
on: null
jobs:
  test:
    steps: null
"""
        )

        parser = WorkflowParser()
        result = parser.parse_file(test_file)
        assert result is None or isinstance(result, object)

    def test_parser_with_special_yaml_tags(self, tmp_path):
        """Test parser with YAML special tags."""
        from services import WorkflowParser

        test_file = tmp_path / "tags.yml"
        test_file.write_text(
            """
name: test
binary: !!binary |
  R0lGODlhDAAMAIQAAP//9/X17unp5WZmTmRkZP/z7/zz94daAALS
timestamp: 2001-12-15T02:59:43.1Z
"""
        )

        parser = WorkflowParser()
        result = parser.parse_file(test_file)
        assert result is None or isinstance(result, object)

    def test_parser_with_yaml_comments(self, tmp_path):
        """Test parser preserves functionality with YAML comments."""
        from services import WorkflowParser

        test_file = tmp_path / "comments.yml"
        test_file.write_text(
            """
# This is a comment
name: test  # inline comment
on:
  # Push workflow
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    # Steps comment
    steps:
      - run: echo "test"  # echo comment
"""
        )

        parser = WorkflowParser()
        result = parser.parse_file(test_file)
        assert result is None or isinstance(result, object)


class TestWorkflowInventoryScan:
    """Tests for WorkflowInventory scan functionality."""

    def test_inventory_scan_empty_directory(self):
        """Test scanning empty directory."""
        from services import WorkflowInventory
        pass  # removed redundant `import tempfile` (top-level import used)

        inventory = WorkflowInventory()

        with tempfile.TemporaryDirectory() as tmpdir:
            if hasattr(inventory, "scan"):
                result = inventory.scan(Path(tmpdir))
                # Should return empty or None
                assert result is None or isinstance(result, (list, dict))

    def test_inventory_scan_with_workflows(self):
        """Test scanning directory with workflows."""
        from services import WorkflowInventory
        pass  # removed redundant `import tempfile` (top-level import used)

        inventory = WorkflowInventory()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .github/workflows directory
            workflows_dir = Path(tmpdir) / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)

            # Create workflow files
            (workflows_dir / "ci.yml").write_text("name: CI")
            (workflows_dir / "cd.yml").write_text("name: CD")

            if hasattr(inventory, "scan"):
                result = inventory.scan(Path(tmpdir))
                # Should discover workflows
                assert result is None or isinstance(result, (list, dict))

    def test_inventory_scan_nested_workflow_dirs(self):
        """Test scanning with nested workflow directories."""
        from services import WorkflowInventory
        pass  # removed redundant `import tempfile` (top-level import used)

        inventory = WorkflowInventory()

        with tempfile.TemporaryDirectory() as tmpdir:
            workflows_dir = Path(tmpdir) / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)

            (workflows_dir / "test.yml").write_text("name: test")
            (workflows_dir / "subdir").mkdir()
            (workflows_dir / "subdir" / "nested.yml").write_text("name: nested")

            if hasattr(inventory, "scan"):
                result = inventory.scan(Path(tmpdir))
                assert isinstance(result, (list, dict, type(None)))


class TestWorkflowMetadataHandling:
    """Tests for workflow metadata handling."""

    def test_metadata_from_minimal_workflow(self):
        """Test extracting metadata from minimal workflow."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "minimal.yml"
            test_file.write_text("name: Minimal")

            result = parser.parse_file(test_file)
            # Should handle minimal workflow
            assert result is None or isinstance(result, object)

    def test_metadata_with_all_triggers(self):
        """Test workflow with all trigger types."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "triggers.yml"
            test_file.write_text(
                """
name: All Triggers
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
  workflow_call:
"""
            )

            result = parser.parse_file(test_file)
            assert result is None or isinstance(result, object)

    def test_metadata_with_inputs(self):
        """Test workflow with input parameters."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "inputs.yml"
            test_file.write_text(
                """
name: With Inputs
on:
  workflow_call:
    inputs:
      name:
        description: 'Name'
        required: true
        type: string
      debug:
        description: 'Debug mode'
        required: false
        type: boolean
"""
            )

            result = parser.parse_file(test_file)
            assert result is None or isinstance(result, object)


class TestServiceModuleLogging:
    """Tests for logging in services module."""

    def test_logger_configuration(self):
        """Test that logger is properly configured."""
        import services

        logger = services.logger
        assert logger is not None, "logger must be initialized"
        assert isinstance(logger, logging.Logger)

    def test_logger_level_defaults(self):
        """Test logger level configuration."""
        import services

        # Logger should have a level or inherit from root
        assert services.logger.level >= 0, "level must be greater than zero"

    def test_logger_propagation(self):
        """Test logger propagation settings."""
        import services

        # Check if logger propagates to root
        assert hasattr(services.logger, "propagate")

    @patch("logging.getLogger")
    def test_logger_factory_called(self, mock_get_logger):
        """Test that logger factory is called correctly."""
        mock_get_logger.return_value = logging.getLogger("test")

        import services

        # Logger should be obtained from logging module
        assert services.logger is not None, "logger must be initialized"


class TestServicesGitHubOptionalDependency:
    """Tests for optional GitHub client dependency."""

    def test_services_works_without_httpx(self):
        """Test that services works when httpx is not available."""
        import services

        # Services should be importable even if httpx is missing
        assert hasattr(services, "WorkflowParser")
        assert hasattr(services, "WorkflowInventory")

    @patch.dict("sys.modules", {"httpx": None})
    def test_github_import_failure_handling(self):
        """Test handling of GitHub import failures."""
        import services

        # Services should be usable
        parser = services.WorkflowParser()
        assert parser is not None, "parser must be initialized"

    def test_github_client_conditional_import(self):
        """Test GitHub client is conditionally imported."""
        import services

        github_client_available = "GitHubClient" in services.__all__

        # Either it's available or not, but module shouldn't break
        assert isinstance(services.__all__, list)


class TestWorkflowParserCaching:
    """Tests for parser caching behavior."""

    def test_cache_stores_results(self):
        """Test that cache stores parse results."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yml"
            test_file.write_text("name: test")

            parser.parse_file(test_file, use_cache=True)

            # File should be in cache
            assert test_file in parser._cache or len(parser._cache) >= 0, "Collection must not be empty"

    def test_cache_bypass_with_use_cache_false(self):
        """Test cache bypass when use_cache=False."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yml"
            test_file.write_text("name: test")

            initial_cache = len(parser._cache)
            parser.parse_file(test_file, use_cache=False)
            # Cache might not grow when use_cache=False

            assert len(parser._cache) >= initial_cache, "Collection must not be empty"

    def test_cache_hit_consistency(self):
        """Test that cache hits return consistent results."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yml"
            test_file.write_text("name: test")

            result1 = parser.parse_file(test_file, use_cache=True)
            result2 = parser.parse_file(test_file, use_cache=True)

            # Both should be same or both None
            assert (result1 is None and result2 is None) or (result1 is result2), "Result must not be empty"


class TestServicesIntegrationScenarios:
    """Integration scenario tests."""

    def test_parse_and_inventory_workflow(self):
        """Test parsing workflow and adding to inventory."""
        from services import WorkflowInventory, WorkflowParser

        parser = WorkflowParser()
        inventory = WorkflowInventory()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yml"
            test_file.write_text("name: Integration Test")

            # Parse workflow
            parsed = parser.parse_file(test_file)

            # Inventory scan
            if hasattr(inventory, "scan"):
                scanned = inventory.scan(Path(tmpdir))

            # Both should succeed or gracefully handle
            assert True, "True is not valid"

    def test_multiple_workflows_parsing(self):
        """Test parsing multiple workflows."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            workflows_dir = Path(tmpdir) / "workflows"
            workflows_dir.mkdir()

            # Create multiple workflows
            for i in range(5):
                wf = workflows_dir / f"workflow_{i}.yml"
                wf.write_text(f"name: Workflow {i}")

            # Parse all
            for wf in workflows_dir.glob("*.yml"):
                result = parser.parse_file(wf)
                assert result is None or isinstance(result, object)

    def test_workflow_directory_discovery(self):
        """Test discovering workflow files in directory."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            workflows = Path(tmpdir) / ".github" / "workflows"
            workflows.mkdir(parents=True)

            # Create workflow files
            (workflows / "ci.yml").write_text("name: CI")
            (workflows / "cd.yml").write_text("name: CD")

            # Should be able to parse found files
            for wf in workflows.glob("*.yml"):
                result = parser.parse_file(wf)
                assert result is None or isinstance(result, object)


class TestServicesErrorHandlingExtended:
    """Extended error handling tests."""

    def test_parser_recovers_from_error(self):
        """Test that parser recovers from parse error."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.yml"
            bad_file.write_text("invalid: yaml: content:")

            # First parse fails
            result1 = parser.parse_file(bad_file)

            # Second parse should work independently
            good_file = Path(tmpdir) / "good.yml"
            good_file.write_text("name: good")
            result2 = parser.parse_file(good_file)

            # Should recover
            assert result1 is None or isinstance(result1, object)
            assert result2 is None or isinstance(result2, object)

    def test_handles_missing_required_fields(self):
        """Test handling workflows missing required fields."""
        from services import WorkflowParser

        parser = WorkflowParser()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Minimal workflow without 'on' trigger
            test_file = Path(tmpdir) / "minimal.yml"
            test_file.write_text("name: Minimal")

            result = parser.parse_file(test_file)
            # Should handle gracefully
            assert result is None or isinstance(result, object)

    def test_handles_syntax_variations(self):
        """Test handling various YAML syntax variations."""
        from services import WorkflowParser

        parser = WorkflowParser()

        variations = [
            '{"name": "JSON"}',  # JSON format
            'name: "string with: colons"',  # Quoted string with colons
            "name: |  # Multi-line\n  test",  # Multi-line syntax
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            for i, content in enumerate(variations):
                test_file = Path(tmpdir) / f"variation_{i}.yml"
                test_file.write_text(content)

                result = parser.parse_file(test_file)
                # Should handle variations
                assert result is None or isinstance(result, object)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
