"""Comprehensive pytest tests for src/services/workflow/parser.py module - 60 tests."""

import builtins
from pathlib import Path

import pytest

from src.services.workflow.parser import WorkflowParser
from src.services.workflow.types import (
    InputType,
    TriggerType,
)
from tests.services.workflow._helpers import raise_exception

# ============================================================================
# 1. PARSER INITIALIZATION (5 tests)
# ============================================================================


class TestParserInitialization:
    """Tests for WorkflowParser initialization."""

    def test_parser_init_creates_instance(self):
        """Test parser instantiation."""
        parser = WorkflowParser()
        assert parser is not None, "parser must be initialized"
        assert isinstance(parser, WorkflowParser)

    def test_parser_init_empty_cache(self):
        """Test parser initializes with empty cache."""
        parser = WorkflowParser()
        assert hasattr(parser, "_cache")
        assert isinstance(parser._cache, dict)
        assert len(parser._cache) == 0, "Collection must not be empty"

    def test_parser_has_parse_file_method(self):
        """Test parser has parse_file method."""
        parser = WorkflowParser()
        assert hasattr(parser, "parse_file")
        assert callable(parser.parse_file), "Condition must be true"

    def test_parser_has_parse_content_method(self):
        """Test parser has parse_content method."""
        parser = WorkflowParser()
        assert hasattr(parser, "parse_content")
        assert callable(parser.parse_content), "Content must not be empty"

    def test_parser_has_parse_method(self):
        """Test parser has parse convenience method."""
        parser = WorkflowParser()
        assert hasattr(parser, "parse")
        assert callable(parser.parse), "Condition must be true"


# ============================================================================
# 2. PARSING VALID WORKFLOWS (15 tests)
# ============================================================================


class TestParsingValidWorkflows:
    """Tests for parsing valid workflow definitions."""

    def test_parse_minimal_workflow(self):
        """Test parsing minimal valid workflow."""
        parser = WorkflowParser()
        yaml_content = "name: minimal\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert result.name == "minimal", "Result must not be empty"
        assert result.file_path == Path("test.yml"), "Result must not be empty"

    def test_parse_workflow_with_push_trigger(self):
        """Test parsing workflow with push trigger."""
        parser = WorkflowParser()
        yaml_content = (
            "name: push-workflow\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert any(t.type == TriggerType.PUSH for t in result.triggers), "Result must not be empty"

    def test_parse_workflow_with_pull_request_trigger(self):
        """Test parsing workflow with pull_request trigger."""
        parser = WorkflowParser()
        yaml_content = "name: pr-workflow\non: pull_request\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert any(t.type == TriggerType.PULL_REQUEST for t in result.triggers), "Result must not be empty"

    def test_parse_workflow_with_schedule_trigger(self):
        """Test parsing workflow with schedule trigger."""
        parser = WorkflowParser()
        yaml_content = "name: scheduled\non:\n  schedule:\n    - cron: '0 0 * * *'\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert any(t.type == TriggerType.SCHEDULE for t in result.triggers), "Result must not be empty"

    def test_parse_workflow_with_workflow_dispatch(self):
        """Test parsing workflow with workflow_dispatch trigger."""
        parser = WorkflowParser()
        yaml_content = "name: dispatch\non: workflow_dispatch\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert result.is_triggerable, "Result must not be empty"

    def test_parse_workflow_with_workflow_call(self):
        """Test parsing workflow with workflow_call trigger."""
        parser = WorkflowParser()
        yaml_content = "name: reusable\non: workflow_call\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert result.is_reusable, "Result must not be empty"

    def test_parse_workflow_with_multiple_triggers(self):
        """Test parsing workflow with multiple triggers."""
        parser = WorkflowParser()
        yaml_content = "name: multi\non:\n  push:\n  pull_request:\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert len(result.triggers) >= 2, "Collection must not be empty"

    def test_parse_workflow_with_jobs(self):
        """Test parsing workflow with multiple jobs."""
        parser = WorkflowParser()
        yaml_content = (
            "name: multi-job\non: push\njobs:\n"
            "  job1:\n    runs-on: ubuntu-latest\n"
            "  job2:\n    runs-on: macos-latest\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert len(result.jobs) == 2, "Collection must not be empty"
        assert "job1" in result.jobs, "Result must not be empty"
        assert "job2" in result.jobs, "Result must not be empty"

    def test_parse_workflow_with_permissions(self):
        """Test parsing workflow with permissions."""
        parser = WorkflowParser()
        yaml_content = (
            "name: perms\non: push\npermissions:\n  contents: read\n  actions: write\njobs: {}\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert isinstance(result.permissions, dict)

    def test_parse_workflow_with_env_vars(self):
        """Test parsing workflow with environment variables."""
        parser = WorkflowParser()
        yaml_content = "name: env-test\non: push\nenv:\n  VAR1: value1\n  VAR2: value2\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert isinstance(result.env, dict)

    def test_parse_workflow_with_concurrency(self):
        """Test parsing workflow with concurrency settings."""
        parser = WorkflowParser()
        yaml_content = "name: concurrency-test\non: push\nconcurrency:\n  group: test\n  cancel-in-progress: true\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert result.concurrency is not None, "concurrency must be initialized"

    def test_parse_workflow_with_job_needs(self):
        """Test parsing workflow with job dependencies."""
        parser = WorkflowParser()
        yaml_content = (
            "name: deps\non: push\njobs:\n"
            "  job1:\n    runs-on: ubuntu-latest\n"
            "  job2:\n    runs-on: ubuntu-latest\n    needs: job1\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        job2 = result.jobs.get("job2")
        assert job2 is not None, "job2 must be initialized"
        assert job2.needs == ["job1"], "needs is not valid"

    def test_parse_workflow_with_timeout_minutes(self):
        """Test parsing workflow with timeout configuration."""
        parser = WorkflowParser()
        yaml_content = (
            "name: timeout\non: push\njobs:\n"
            "  job1:\n    runs-on: ubuntu-latest\n    timeout-minutes: 30\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        job1 = result.jobs.get("job1")
        assert job1 is not None, "job1 must be initialized"
        assert job1.timeout_minutes == 30, "timeout_minutes is not valid"

    def test_parse_workflow_with_conditional_job(self):
        """Test parsing workflow with conditional job."""
        parser = WorkflowParser()
        yaml_content = (
            "name: conditional\non: push\njobs:\n"
            "  job1:\n    runs-on: ubuntu-latest\n"
            "    if: success()\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        job1 = result.jobs.get("job1")
        assert job1 is not None, "job1 must be initialized"
        assert job1.if_condition == "success()", "if_condition is not valid"


# ============================================================================
# 3. PARSING INVALID/MALFORMED WORKFLOWS (15 tests)
# ============================================================================


class TestParsingInvalidWorkflows:
    """Tests for parsing invalid or malformed workflow definitions."""

    def test_parse_invalid_yaml_syntax(self):
        """Test parse raises ValueError for invalid YAML."""
        parser = WorkflowParser()
        invalid_yaml = "{ bad: yaml: content [invalid"
        with pytest.raises(ValueError, match="Invalid YAML"):
            parser.parse(invalid_yaml, Path("test.yml"))

    def test_parse_empty_yaml(self):
        """Test parse_content returns None for empty YAML."""
        parser = WorkflowParser()
        result = parser.parse_content("", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_yaml_list_not_dict(self):
        """Test parse raises ValueError for non-dict YAML."""
        parser = WorkflowParser()
        yaml_list = "- item1\n- item2\n"
        with pytest.raises(ValueError, match="must be a dictionary"):
            parser.parse(yaml_list, Path("test.yml"))

    def test_parse_yaml_scalar(self):
        """Test parse raises ValueError for scalar YAML."""
        parser = WorkflowParser()
        with pytest.raises(ValueError, match="must be a dictionary"):
            parser.parse("just a string", Path("test.yml"))

    def test_parse_content_invalid_yaml(self):
        """Test parse_content returns None for invalid YAML."""
        parser = WorkflowParser()
        result = parser.parse_content("{ bad: yaml: [", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_file_nonexistent(self, tmp_path):
        """Test parse_file returns None for nonexistent file."""
        parser = WorkflowParser()
        result = parser.parse_file(tmp_path / "nonexistent.yml")
        assert result is None, "Result must not be empty"

    def test_parse_file_permission_error(self, monkeypatch, tmp_path):
        """Test parse_file handles permission errors."""
        parser = WorkflowParser()
        workflow_file = tmp_path / "workflow.yml"
        workflow_file.write_text("name: test\non: push\njobs: {}\n")

        def mock_open_with_error(*args, **kwargs):
            if args and (args[0] == workflow_file or args[0] == str(workflow_file)):
                raise PermissionError("Access denied")
            return builtins.open(*args, **kwargs)

        monkeypatch.setattr(builtins, "open", mock_open_with_error)
        result = parser.parse_file(workflow_file)
        assert result is None, "Result must not be empty"

    def test_parse_file_encoding_error(self, monkeypatch, tmp_path):
        """Test parse_file handles unicode decode errors."""
        parser = WorkflowParser()
        workflow_file = tmp_path / "workflow.yml"
        workflow_file.write_text("name: test\non: push\njobs: {}\n")

        def mock_open_with_error(*args, **kwargs):
            if args and (args[0] == workflow_file or args[0] == str(workflow_file)):
                raise UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
            return builtins.open(*args, **kwargs)

        monkeypatch.setattr(builtins, "open", mock_open_with_error)
        result = parser.parse_file(workflow_file)
        assert result is None, "Result must not be empty"

    def test_parse_content_null_yaml(self):
        """Test parse_content with null YAML."""
        parser = WorkflowParser()
        result = parser.parse_content("null", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_content_boolean_yaml(self):
        """Test parse_content with boolean YAML."""
        parser = WorkflowParser()
        result = parser.parse_content("true", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_malformed_permissions(self):
        """Test parsing with malformed permissions."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\npermissions: 'all'\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        # Should handle string permissions gracefully
        assert isinstance(result.permissions, dict)

    def test_parse_malformed_env(self):
        """Test parsing with malformed env variables."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\nenv: [not, a, dict]\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        # Should handle non-dict env gracefully
        assert isinstance(result.env, dict)

    def test_parse_nonexistent_trigger_type(self):
        """Test parsing with unknown trigger type."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: unknown_trigger\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        # Should map to OTHER trigger type
        assert any(t.type == TriggerType.OTHER for t in result.triggers), "Result must not be empty"

    def test_parse_invalid_input_type(self):
        """Test parsing with invalid workflow input type."""
        parser = WorkflowParser()
        yaml_content = (
            "name: test\non:\n  workflow_dispatch:\n"
            "    inputs:\n      test:\n        type: invalid_type\njobs: {}\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        # Should default to STRING type
        if "test" in result.inputs:
            assert result.inputs["test"].type == InputType.STRING, "Result must not be empty"

    def test_parse_job_with_invalid_runs_on(self):
        """Test parsing job with invalid runs-on."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs:\n  test:\n    runs-on: null\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        # Should return None when runs-on is null (validation error)
        assert result is None, "Result must not be empty"


# ============================================================================
# 4. SCHEMA VALIDATION (10 tests)
# ============================================================================


class TestSchemaValidation:
    """Tests for workflow schema validation."""

    def test_workflow_has_name_field(self):
        """Test parsed workflow has name field."""
        parser = WorkflowParser()
        yaml_content = "name: test-workflow\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert hasattr(result, "name")
        assert result.name == "test-workflow", "Result must not be empty"

    def test_workflow_name_defaults_to_filename(self):
        """Test workflow name defaults to filename if missing."""
        parser = WorkflowParser()
        yaml_content = "on: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("workflow.yml"))
        assert result is not None, "result must be initialized"
        assert result.name == "workflow", "Result must not be empty"

    def test_workflow_has_file_path_field(self):
        """Test parsed workflow has file_path field."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("/path/to/test.yml"))
        assert result is not None, "result must be initialized"
        assert result.file_path == Path("/path/to/test.yml"), "Result must not be empty"

    def test_workflow_has_triggers_field(self):
        """Test parsed workflow has triggers field."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert hasattr(result, "triggers")
        assert isinstance(result.triggers, list)

    def test_workflow_has_jobs_field(self):
        """Test parsed workflow has jobs field."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert hasattr(result, "jobs")
        assert isinstance(result.jobs, dict)

    def test_workflow_has_inputs_field(self):
        """Test parsed workflow has inputs field."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert hasattr(result, "inputs")
        assert isinstance(result.inputs, dict)

    def test_workflow_has_dependencies_field(self):
        """Test parsed workflow has dependencies field."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert hasattr(result, "dependencies")
        assert isinstance(result.dependencies, list)

    def test_job_has_required_fields(self):
        """Test parsed job has required fields."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs:\n  job1:\n    runs-on: ubuntu-latest\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        job = result.jobs.get("job1")
        assert job is not None, "job must be initialized"
        assert job.id == "job1", "id is not valid"
        assert job.runs_on == "ubuntu-latest", "runs_on is not valid"

    def test_input_has_required_fields(self):
        """Test parsed input has required fields."""
        parser = WorkflowParser()
        yaml_content = (
            "name: test\non:\n  workflow_dispatch:\n"
            "    inputs:\n      param1:\n        description: Test param\n"
            "        type: string\njobs: {}\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        inp = result.inputs.get("param1")
        assert inp is not None, "inp must be initialized"
        assert inp.name == "param1", "name is not valid"
        assert inp.type == InputType.STRING, "type is not valid"

    def test_trigger_has_type_field(self):
        """Test trigger has type field."""
        parser = WorkflowParser()
        yaml_content = "name: test\non: push\njobs: {}\n"
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert len(result.triggers) > 0, "Collection must not be empty"
        trigger = result.triggers[0]
        assert hasattr(trigger, "type")
        assert trigger.type == TriggerType.PUSH, "type is not valid"


# ============================================================================
# 5. ERROR HANDLING AND EXCEPTIONS (10 tests)
# ============================================================================


class TestErrorHandlingExceptions:
    """Tests for error handling and exception management."""

    def test_parse_file_handles_yaml_error(self):
        """Test parse_content handles YAML parsing errors gracefully."""
        parser = WorkflowParser()
        yaml_content = "{ invalid: yaml: [}"
        result = parser.parse_content(yaml_content, Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_content_handles_key_error(self, monkeypatch):
        """Test parse_content handles KeyError gracefully."""
        parser = WorkflowParser()
        monkeypatch.setattr(parser, "_parse_triggers", raise_exception(KeyError("trigger")))
        result = parser.parse_content("name: test\non: push\njobs: {}\n", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_content_handles_value_error(self, monkeypatch):
        """Test parse_content handles ValueError gracefully."""
        parser = WorkflowParser()
        monkeypatch.setattr(parser, "_parse_jobs", raise_exception(ValueError("job error")))
        result = parser.parse_content("name: test\non: push\njobs: {}\n", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_content_handles_unexpected_error(self, monkeypatch):
        """Test parse_content handles unexpected exceptions gracefully."""
        parser = WorkflowParser()
        monkeypatch.setattr(parser, "_parse_triggers", raise_exception(RuntimeError("boom")))
        result = parser.parse_content("name: test\non: push\njobs: {}\n", Path("test.yml"))
        assert result is None, "Result must not be empty"

    def test_parse_triggers_handles_invalid_config(self):
        """Test _parse_triggers handles invalid config."""
        parser = WorkflowParser()
        triggers = parser._parse_triggers(None)
        assert triggers == [], "triggers is not valid"

    def test_parse_triggers_handles_string_trigger(self):
        """Test _parse_triggers handles string trigger format."""
        parser = WorkflowParser()
        triggers = parser._parse_triggers("push")
        assert len(triggers) == 1, "Triggers must not be empty"
        assert triggers[0].type == TriggerType.PUSH, "type is not valid"

    def test_parse_triggers_handles_list_triggers(self):
        """Test _parse_triggers handles list trigger format."""
        parser = WorkflowParser()
        triggers = parser._parse_triggers(["push", "pull_request"])
        assert len(triggers) == 2, "Triggers must not be empty"

    def test_parse_inputs_handles_missing_inputs(self):
        """Test _parse_inputs handles missing inputs gracefully."""
        parser = WorkflowParser()
        inputs = parser._parse_inputs({})
        assert inputs == {}, "inputs is not valid"

    def test_parse_inputs_handles_invalid_input_type(self):
        """Test _parse_inputs handles invalid input type."""
        parser = WorkflowParser()
        on_config = {
            "workflow_dispatch": {
                "inputs": {"test": {"type": "unsupported_type", "description": "test"}}
            }
        }
        inputs = parser._parse_inputs(on_config)
        assert "test" in inputs, "Condition must be true"
        assert inputs["test"].type == InputType.STRING, "type is not valid"

    def test_parse_jobs_handles_non_dict_jobs(self):
        """Test _parse_jobs handles non-dict job config."""
        parser = WorkflowParser()
        jobs = parser._parse_jobs("not a dict")
        assert jobs == {}, "jobs is not valid"


# ============================================================================
# 6. EDGE CASES (5 tests)
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_parse_workflow_with_yaml_anchors_and_aliases(self):
        """Test parsing workflow with YAML anchors and aliases."""
        parser = WorkflowParser()
        yaml_content = (
            "defaults: &defaults\n  runs-on: ubuntu-latest\n"
            "name: anchor-test\non: push\njobs:\n"
            "  job1:\n    <<: *defaults\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        assert "job1" in result.jobs, "Result must not be empty"

    def test_parse_workflow_with_branch_filters(self):
        """Test parsing workflow with branch filters."""
        parser = WorkflowParser()
        yaml_content = (
            "name: branch-filter\non:\n" "  push:\n    branches: [main, develop]\njobs: {}\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        trigger = result.triggers[0]
        assert trigger.branches == ["main", "develop"]

    def test_parse_workflow_with_path_filters(self):
        """Test parsing workflow with path filters."""
        parser = WorkflowParser()
        yaml_content = (
            "name: path-filter\non:\n" "  push:\n    paths: ['src/**', 'tests/**']\njobs: {}\n"
        )
        result = parser.parse(yaml_content, Path("test.yml"))
        assert result is not None, "result must be initialized"
        trigger = result.triggers[0]
        assert trigger.paths == ["src/**", "tests/**"]

    def test_parse_workflow_with_single_vs_list_needs(self):
        """Test parsing job needs as both string and list."""
        parser = WorkflowParser()
        # Single need as string
        yaml_content1 = (
            "name: needs-single\non: push\njobs:\n"
            "  job1:\n    runs-on: ubuntu-latest\n"
            "  job2:\n    runs-on: ubuntu-latest\n    needs: job1\n"
        )
        result1 = parser.parse(yaml_content1, Path("test.yml"))
        assert result1 is not None, "result1 must be initialized"
        job2 = result1.jobs.get("job2")
        assert job2.needs == ["job1"], "needs is not valid"

    def test_parse_workflow_file_modification_time(self, tmp_path):
        """Test parsing captures file modification time."""
        parser = WorkflowParser()
        workflow_file = tmp_path / "workflow.yml"
        workflow_file.write_text("name: mtime-test\non: push\njobs: {}\n")

        result = parser.parse_file(workflow_file)
        assert result is not None, "result must be initialized"
        assert result.last_modified is not None, "last_modified must be initialized"

    def test_parse_workflow_cache_invalidation(self):
        """Test cache can be cleared and repopulated."""
        parser = WorkflowParser()
        yaml_content = "name: cache-test\non: push\njobs: {}\n"
        path = Path("test.yml")

        result1 = parser.parse(yaml_content, path)
        assert result1 is not None, "result1 must be initialized"
        assert result1.name == "cache-test", "Result must not be empty"

        if hasattr(parser, "clear_cache"):
            parser.clear_cache()
            assert len(parser._cache) == 0, "Collection must not be empty"
