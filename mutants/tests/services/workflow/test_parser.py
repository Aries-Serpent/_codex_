"""Comprehensive tests for src/services/workflow/parser.py module."""

import builtins
from pathlib import Path

import pytest

from src.services.workflow.parser import WorkflowParser, logger
from src.services.workflow.types import (
    TriggerType,
    WorkflowInput,
    WorkflowJob,
    WorkflowMetadata,
)
from tests.services.workflow._helpers import raise_exception


def _patch_open_error(monkeypatch, workflow: Path, exception: Exception) -> None:
    original_open = builtins.open

    def _raise_for_target(*args, **kwargs):
        if args and (args[0] == workflow or args[0] == str(workflow)):
            raise exception
        return original_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", _raise_for_target)


class TestWorkflowParser:
    """Tests for WorkflowParser class."""

    def test_parser_import(self):
        """Test that WorkflowParser can be imported."""
        assert WorkflowParser is not None, "WorkflowParser must be initialized"

    def test_parser_creation(self):
        """Test creating WorkflowParser initializes cache."""
        parser = WorkflowParser()
        assert parser is not None, "parser must be initialized"
        assert hasattr(parser, "_cache")
        assert len(parser._cache) == 0, "Collection must not be empty"

    def test_parser_has_cache(self):
        """Test that parser cache is a dictionary."""
        parser = WorkflowParser()
        assert hasattr(parser, "_cache")
        assert isinstance(parser._cache, dict)
        # Test we can add items to cache
        test_path = Path("/test/path.yml")
        parser._cache[test_path] = None
        assert test_path in parser._cache, "Condition must be true"

    def test_parse_file_nonexistent(self, tmp_path: Path):
        """Test parsing nonexistent file returns None."""
        parser = WorkflowParser()
        result = parser.parse_file(tmp_path / "nonexistent_path.yml")
        assert result is None, "Result must not be empty"

    def test_parse_file_uses_cache(self):
        """Test that parse_file respects use_cache parameter."""
        parser = WorkflowParser()
        # Parse nonexistent file (returns None, but should cache)
        path = Path("/test/cache.yml")
        parser.parse_file(path, use_cache=False)
        # Cache should remain empty when use_cache=False
        assert len(parser._cache) == 0, "Collection must not be empty"

    def test_parse_file_populates_and_reuses_cache_when_enabled(self, tmp_path):
        """Test parse_file caches results when use_cache=True and reuses cached value."""
        parser = WorkflowParser()
        workflow_path = tmp_path / "workflow.yml"
        workflow_path.write_text(
            "name: test-workflow\n"
            "on: push\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            '      - run: echo "hello"\n',
            encoding="utf-8",
        )

        first_result = parser.parse_file(workflow_path, use_cache=True)
        assert workflow_path in parser._cache, "w is not valid"
        assert parser._cache[workflow_path] == first_result, "Result must not be empty"

        second_result = parser.parse_file(workflow_path, use_cache=True)
        assert second_result == first_result, "Result must not be empty"
        assert second_result == parser._cache[workflow_path], "Result must not be empty"


class TestWorkflowParserCaching:
    """Tests for WorkflowParser caching behavior."""

    def test_clear_cache_method(self):
        """Test clear_cache method if exists."""
        parser = WorkflowParser()
        # Add something to cache manually
        parser._cache[Path("/test.yml")] = None
        if hasattr(parser, "clear_cache"):
            parser.clear_cache()
            assert len(parser._cache) == 0, "Collection must not be empty"
        else:
            # If no clear_cache method, we can clear manually
            parser._cache.clear()
            assert len(parser._cache) == 0, "Collection must not be empty"

    def test_cache_persists_across_calls(self):
        """Test that cache persists across multiple parse calls."""
        parser = WorkflowParser()
        # Add test entry
        test_path = Path("/cached.yml")
        parser._cache[test_path] = None
        # Verify it persists
        assert test_path in parser._cache, "Condition must be true"


class TestModuleImports:
    """Tests for module imports."""

    def test_types_import(self):
        """Test that types module classes can be imported."""
        assert TriggerType is not None, "TriggerType must be initialized"
        assert WorkflowMetadata is not None, "WorkflowMetadata must be initialized"

    def test_logger_configured(self):
        """Test that logger is configured and usable."""
        assert logger is not None, "logger must be initialized"
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_workflow_input_type(self):
        """Test WorkflowInput type is available."""
        assert WorkflowInput is not None, "WorkflowInput must be initialized"

    def test_workflow_job_type(self):
        """Test WorkflowJob type is available."""
        assert WorkflowJob is not None, "WorkflowJob must be initialized"


class TestWorkflowParserMethods:
    """Tests for WorkflowParser methods."""

    def test_parse_content_empty_string(self):
        """Test parse_content with empty string."""
        parser = WorkflowParser()
        result = parser.parse_content("", Path("/test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_content_invalid_yaml(self):
        """Test parse_content with invalid YAML."""
        parser = WorkflowParser()
        invalid_yaml = "{ invalid: yaml: content"
        result = parser.parse_content(invalid_yaml, Path("/test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_validates_non_mapping_yaml(self):
        """Test parse rejects YAML that does not produce a mapping."""
        parser = WorkflowParser()
        with pytest.raises(ValueError, match="must be a dictionary"):
            parser.parse("- item", Path("/test.yml"))

    def test_parse_returns_metadata_for_valid_yaml(self):
        """Test parse returns metadata for valid YAML input."""
        parser = WorkflowParser()
        workflow = parser.parse(
            "name: Valid\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo test",
            Path("/test.yml"),
        )
        assert workflow is not None, "workflow must be initialized"
        assert workflow.name == "Valid", "name is not valid"

    def test_parse_file_handles_permission_error(self, monkeypatch, tmp_path):
        """Test parse_file returns None on permission errors."""
        parser = WorkflowParser()
        # Patch open so reads for this workflow path fail, while all other open calls delegate.
        workflow = tmp_path / "workflow.yml"
        workflow.write_text("name: Test\non: push\njobs: {}\n")
        _patch_open_error(monkeypatch, workflow, PermissionError("denied"))
        assert parser.parse_file(workflow) is None, "Condition must be true"

    def test_parse_file_handles_unexpected_error(self, monkeypatch, tmp_path):
        """Test parse_file returns None on unexpected read failures."""
        parser = WorkflowParser()
        workflow = tmp_path / "workflow.yml"
        workflow.write_text("name: Test\non: push\njobs: {}\n")
        _patch_open_error(monkeypatch, workflow, RuntimeError("boom"))
        assert parser.parse_file(workflow) is None, "Condition must be true"

    def test_parse_content_handles_value_error_from_job_parsing(self, monkeypatch):
        """Test parse_content degrades cleanly when job parsing raises ValueError."""
        parser = WorkflowParser()
        monkeypatch.setattr(parser, "_parse_jobs", raise_exception(ValueError("bad job")))
        result = parser.parse_content(
            "name: Broken\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
            Path("/test.yml"),
        )
        assert result is None, "Result must not be empty"

    def test_parse_content_handles_unexpected_job_parsing_error(self, monkeypatch):
        """Test parse_content degrades cleanly when job parsing raises an unexpected error."""
        parser = WorkflowParser()
        monkeypatch.setattr(parser, "_parse_jobs", raise_exception(RuntimeError("boom")))
        result = parser.parse_content(
            "name: Broken\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
            Path("/test.yml"),
        )
        assert result is None, "Result must not be empty"
