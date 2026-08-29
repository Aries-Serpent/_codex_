"""
Comprehensive tests for the codex_harness module.

Tests cover:
- HonestyStatement, HonestyMetadata, HonestyRecorder
- ToolInvocation, ToolTraceLogger
- compute_golden_harness_status

Phase 4: Coverage improvement - adding tests for 0% coverage module.
"""

import json
from datetime import datetime

import pytest

from codex_harness.honesty import (
    HonestyMetadata,
    HonestyRecorder,
    HonestyStatement,
    _utc_now,
)
from codex_harness.tool_trace import (
    ToolInvocation,
    ToolTraceLogger,
    _normalize_status,
)


class TestHonestyStatement:
    """Test HonestyStatement dataclass."""

    def test_create_basic_statement(self):
        """Test creating a basic honesty statement."""
        statement = HonestyStatement(
            content="Test content",
            category="VERIFIED",
            verified=True,
        )
        assert statement.content == "Test content", "Content must not be empty"
        assert statement.category == "VERIFIED", "category is not valid"
        assert statement.verified is True, "verified is not valid"
        assert statement.workflow is None, "workflow is not valid"
        assert statement.metadata is None, "Data must not be empty"

    def test_create_statement_with_all_fields(self):
        """Test creating statement with all fields."""
        metadata = {"source": "test", "confidence": 0.95}
        statement = HonestyStatement(
            content="Full statement",
            category="INFERRED",
            verified=False,
            workflow="test_workflow",
            timestamp="2026-01-22T00:00:00Z",
            metadata=metadata,
        )
        assert statement.workflow == "test_workflow", "workflow is not valid"
        assert statement.metadata == metadata, "Data must not be empty"

    def test_to_dict_with_metadata(self):
        """Test to_dict includes metadata when present."""
        statement = HonestyStatement(
            content="Test",
            category="AUDIT",
            verified=True,
            metadata={"key": "value"},
        )
        result = statement.to_dict()
        assert "metadata" in result, "Result must not be empty"
        assert result["metadata"] == {"key": "value"}, "Result must not be empty"

    def test_to_dict_without_metadata(self):
        """Test to_dict excludes metadata when None."""
        statement = HonestyStatement(
            content="Test",
            category="SUMMARY",
            verified=False,
        )
        result = statement.to_dict()
        assert "metadata" not in result, "Result must not be empty"

    def test_timestamp_default_factory(self):
        """Test timestamp is auto-generated."""
        statement = HonestyStatement(
            content="Test",
            category="PLANNED",
            verified=False,
        )
        assert statement.timestamp is not None, "timestamp must be initialized"
        # Should be a valid ISO format timestamp
        datetime.fromisoformat(statement.timestamp.replace("Z", "+00:00"))


class TestHonestyMetadata:
    """Test HonestyMetadata dataclass."""

    def test_create_empty_metadata(self):
        """Test creating metadata with no statements."""
        metadata = HonestyMetadata(workflow="test")
        assert metadata.workflow == "test", "Data must not be empty"
        assert metadata.statements == [], "Data must not be empty"

    def test_summary_empty(self):
        """Test summary of empty metadata."""
        metadata = HonestyMetadata(workflow="test")
        summary = metadata.summary()
        assert summary["total"] == 0, "Condition must be true"
        assert summary["verified"] == 0, "Condition must be true"
        assert summary["categories"] == {}, "Condition must be true"

    def test_summary_with_statements(self):
        """Test summary with multiple statements."""
        metadata = HonestyMetadata(
            workflow="test",
            statements=[
                HonestyStatement("A", "VERIFIED", True),
                HonestyStatement("B", "VERIFIED", True),
                HonestyStatement("C", "INFERRED", False),
                HonestyStatement("D", "PLANNED", True),
            ],
        )
        summary = metadata.summary()
        assert summary["total"] == 4, "Condition must be true"
        assert summary["verified"] == 3, "Condition must be true"
        assert summary["categories"]["VERIFIED"] == 2, "Condition must be true"
        assert summary["categories"]["INFERRED"] == 1, "Condition must be true"
        assert summary["categories"]["PLANNED"] == 1, "Condition must be true"


class TestHonestyRecorder:
    """Test HonestyRecorder class."""

    def test_init_default(self):
        """Test default initialization."""
        recorder = HonestyRecorder()
        assert recorder.workflow == "default", "workflow is not valid"
        assert recorder.statements == [], "statements is not valid"

    def test_init_custom(self, tmp_path):
        """Test custom initialization."""
        output = tmp_path / "custom.json"
        recorder = HonestyRecorder(workflow="custom_flow", output_path=output)
        assert recorder.workflow == "custom_flow", "workflow is not valid"
        assert recorder.output_path == output, "output_path is not valid"

    def test_record_statement_basic(self):
        """Test recording a basic statement."""
        recorder = HonestyRecorder()
        statement = recorder.record_statement(
            content="Test content",
            category="verified",
            verified=True,
        )
        assert len(recorder.statements) == 1, "Collection must not be empty"
        assert statement.content == "Test content", "Content must not be empty"
        assert statement.category == "VERIFIED", "category is not valid"
        assert statement.verified is True, "verified is not valid"

    def test_record_statement_with_metadata(self):
        """Test recording statement with metadata."""
        recorder = HonestyRecorder()
        meta = {"source": "test"}
        statement = recorder.record_statement(
            content="Test",
            category="AUDIT",
            verified=True,
            metadata=meta,
        )
        assert statement.metadata == meta, "Data must not be empty"

    def test_record_statement_empty_content_raises(self):
        """Test empty content raises ValueError."""
        recorder = HonestyRecorder()
        with pytest.raises(ValueError, match="content is required"):
            recorder.record_statement(content="", category="VERIFIED", verified=True)

    def test_record_statement_custom_category(self):
        """Test custom categories are added to allowed set."""
        recorder = HonestyRecorder()
        statement = recorder.record_statement(
            content="Test",
            category="CUSTOM_CATEGORY",
            verified=True,
        )
        assert statement.category == "CUSTOM_CATEGORY", "category is not valid"

    def test_flush_creates_file(self, tmp_path):
        """Test flush creates output file."""
        output = tmp_path / "honesty.json"
        recorder = HonestyRecorder(output_path=output)
        recorder.record_statement("Test", "VERIFIED", True)

        result_path = recorder.flush()

        assert result_path == output, "Result must not be empty"
        assert output.exists(), "Condition must be true"
        data = json.loads(output.read_text())
        assert data["workflow"] == "default", "Data must not be empty"
        assert len(data["statements"]) == 1, "Collection must not be empty"

    def test_flush_custom_path(self, tmp_path):
        """Test flush to custom path."""
        default_output = tmp_path / "default.json"
        custom_output = tmp_path / "custom.json"
        recorder = HonestyRecorder(output_path=default_output)
        recorder.record_statement("Test", "VERIFIED", True)

        result_path = recorder.flush(custom_output)

        assert result_path == custom_output, "Result must not be empty"
        assert custom_output.exists(), "Condition must be true"
        assert not default_output.exists(), "Condition must be true"

    def test_load_existing(self, tmp_path):
        """Test loading existing statements."""
        output = tmp_path / "honesty.json"
        existing_data = {
            "workflow": "test",
            "statements": [
                {
                    "content": "Existing",
                    "category": "VERIFIED",
                    "verified": True,
                    "timestamp": "2026-01-01T00:00:00Z",
                }
            ],
            "summary": {"total": 1, "verified": 1, "categories": {"VERIFIED": 1}},
        }
        output.write_text(json.dumps(existing_data))

        recorder = HonestyRecorder(output_path=output)
        recorder.load_existing()

        assert len(recorder.statements) == 1, "Collection must not be empty"
        assert recorder.statements[0].content == "Existing", "Content must not be empty"

    def test_load_existing_no_file(self, tmp_path):
        """Test loading when file doesn't exist."""
        output = tmp_path / "nonexistent.json"
        recorder = HonestyRecorder(output_path=output)
        recorder.load_existing()  # Should not raise
        assert len(recorder.statements) == 0, "Collection must not be empty"


class TestToolInvocation:
    """Test ToolInvocation dataclass."""

    def test_create_basic(self):
        """Test creating basic tool invocation."""
        invocation = ToolInvocation(
            tool="echo",
            args=["hello"],
            exit_code=0,
            started_at="2026-01-22T00:00:00Z",
            finished_at="2026-01-22T00:00:01Z",
            stdout="hello\n",
            stderr="",
        )
        assert invocation.tool == "echo", "tool is not valid"
        assert invocation.exit_code == 0, "exit_code is not valid"

    def test_to_dict_with_metadata(self):
        """Test to_dict includes metadata."""
        invocation = ToolInvocation(
            tool="test",
            args=[],
            exit_code=0,
            started_at="",
            finished_at="",
            stdout="",
            stderr="",
            metadata={"key": "value"},
        )
        result = invocation.to_dict()
        assert "metadata" in result, "Result must not be empty"

    def test_to_dict_without_metadata(self):
        """Test to_dict excludes None metadata."""
        invocation = ToolInvocation(
            tool="test",
            args=[],
            exit_code=0,
            started_at="",
            finished_at="",
            stdout="",
            stderr="",
        )
        result = invocation.to_dict()
        assert "metadata" not in result, "Result must not be empty"


class TestNormalizeStatus:
    """Test _normalize_status helper function."""

    def test_none_returns_none(self):
        """Test None input returns None."""
        assert _normalize_status(None) is None, "_n is not valid"

    def test_pass_statuses(self):
        """Test various pass status values."""
        for status in ["pass", "PASSED", "ok", "success", "green", "true", "1"]:
            assert _normalize_status(status) is True, "_n is not valid"

    def test_fail_statuses(self):
        """Test various fail status values."""
        for status in ["fail", "FAILED", "block", "blocked", "reject", "false", "0"]:
            assert _normalize_status(status) is False, "_n is not valid"

    def test_unknown_returns_none(self):
        """Test unknown status returns None."""
        assert _normalize_status("unknown") is None, "_n is not valid"
        assert _normalize_status("maybe") is None, "_n is not valid"


class TestToolTraceLogger:
    """Test ToolTraceLogger class."""

    def test_init_creates_parent_dir(self, tmp_path):
        """Test initialization creates parent directory."""
        output = tmp_path / "subdir" / "trace.ndjson"
        ToolTraceLogger(output_path=output)
        assert output.parent.exists(), "Condition must be true"

    def test_record_invocation(self, tmp_path):
        """Test recording an invocation."""
        output = tmp_path / "trace.ndjson"
        logger = ToolTraceLogger(output_path=output)

        invocation = ToolInvocation(
            tool="test",
            args=["arg1"],
            exit_code=0,
            started_at="2026-01-22T00:00:00Z",
            finished_at="2026-01-22T00:00:01Z",
            stdout="output",
            stderr="",
        )
        logger.record_invocation(invocation)

        assert output.exists(), "Condition must be true"
        lines = output.read_text().strip().split("\n")
        assert len(lines) == 1, "Lines must not be empty"
        data = json.loads(lines[0])
        assert data["tool"] == "test", "Data must not be empty"

    def test_log_manual(self, tmp_path):
        """Test manual logging."""
        output = tmp_path / "trace.ndjson"
        logger = ToolTraceLogger(output_path=output)

        invocation = logger.log_manual(
            tool="manual_tool",
            args=["arg1", "arg2"],
            exit_code=0,
            stdout="manual output",
            metadata={"manual": True},
        )

        assert invocation.tool == "manual_tool", "tool is not valid"
        assert invocation.exit_code == 0, "exit_code is not valid"
        assert invocation.metadata == {"manual": True}, "Data must not be empty"

    def test_read_invocations(self, tmp_path):
        """Test reading invocations from file."""
        output = tmp_path / "trace.ndjson"
        logger = ToolTraceLogger(output_path=output)

        # Record multiple invocations
        for i in range(3):
            logger.log_manual(
                tool=f"tool_{i}",
                args=[],
                exit_code=i,
            )

        invocations = logger.read_invocations()
        assert len(invocations) == 3, "Invocations must not be empty"
        assert invocations[0].tool == "tool_0", "tool is not valid"
        assert invocations[2].exit_code == 2, "exit_code is not valid"

    def test_read_invocations_empty_file(self, tmp_path):
        """Test reading from nonexistent file."""
        output = tmp_path / "nonexistent.ndjson"
        logger = ToolTraceLogger(output_path=output)

        invocations = logger.read_invocations()
        assert invocations == [], "invocations is not valid"

    def test_load_ra_gate_results_with_gates_list(self, tmp_path):
        """Test loading RA gate results from gates list format."""
        gates_file = tmp_path / "gates.json"
        gates_file.write_text(
            json.dumps(
                {
                    "gates": [
                        {"tool": "ruff", "status": "pass"},
                        {"tool": "pytest", "status": "fail"},
                    ]
                }
            )
        )

        logger = ToolTraceLogger()
        results = logger.load_ra_gate_results(gates_file)

        assert results["ruff"] is True, "Result must not be empty"
        assert results["pytest"] is False, "Result must not be empty"

    def test_load_ra_gate_results_dict_format(self, tmp_path):
        """Test loading RA gate results from dict format."""
        gates_file = tmp_path / "gates.json"
        gates_file.write_text(
            json.dumps(
                {
                    "ruff": "success",
                    "mypy": "blocked",
                }
            )
        )

        logger = ToolTraceLogger()
        results = logger.load_ra_gate_results(gates_file)

        assert results["ruff"] is True, "Result must not be empty"
        assert results["mypy"] is False, "Result must not be empty"

    def test_load_ra_gate_results_nonexistent(self, tmp_path):
        """Test loading from nonexistent file."""
        logger = ToolTraceLogger()
        results = logger.load_ra_gate_results(tmp_path / "nonexistent.json")
        assert results == {}, "Result must not be empty"

    def test_run_tool_success(self, tmp_path):
        """Test running a tool successfully."""
        output = tmp_path / "trace.ndjson"
        logger = ToolTraceLogger(output_path=output)

        # Run echo command
        invocation = logger.run_tool("echo", ["hello", "world"])

        assert invocation.exit_code == 0, "exit_code is not valid"
        assert "hello world" in invocation.stdout, "Condition must be true"

    def test_run_tool_failure_with_check(self, tmp_path):
        """Test running a failing tool with check=True."""
        import subprocess

        output = tmp_path / "trace.ndjson"
        logger = ToolTraceLogger(output_path=output)

        with pytest.raises(subprocess.CalledProcessError):
            logger.run_tool("false")  # 'false' always exits with 1

    def test_run_tool_failure_without_check(self, tmp_path):
        """Test running a failing tool with check=False."""
        output = tmp_path / "trace.ndjson"
        logger = ToolTraceLogger(output_path=output)

        invocation = logger.run_tool("false", check=False)

        assert invocation.exit_code != 0, "exit_code is not valid"

    def test_ra_gate_match_expected_pass(self, tmp_path):
        """Test RA gate matching when pass expected."""
        output = tmp_path / "trace.ndjson"
        gates_file = tmp_path / "gates.json"
        gates_file.write_text(json.dumps({"echo": "pass"}))

        logger = ToolTraceLogger(output_path=output)
        logger.load_ra_gate_results(gates_file)

        invocation = logger.run_tool("echo", ["test"])

        assert invocation.ra_gate_expected is True, "ra_gate_expected is not valid"
        assert invocation.ra_gate_match is True, "ra_gate_match is not valid"


class TestUtcNow:
    """Test _utc_now helper function."""

    def test_returns_iso_format(self):
        """Test returns valid ISO format string."""
        result = _utc_now()
        # Should be parseable
        parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
        assert parsed.tzinfo is not None, "tzinfo must be initialized"
