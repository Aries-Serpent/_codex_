"""
Comprehensive tests for codex.autonomy.audit module.

Tests cover AuditRecord, MetricsSnapshot, and AuditLogger classes with
complete coverage of all public methods and edge cases.
"""

from __future__ import annotations

import json
import logging
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from codex.autonomy.audit import AuditLogger, AuditRecord, MetricsSnapshot
from codex.autonomy.registry import AutonomyMode


class TestAuditRecord:
    """Test AuditRecord dataclass creation and serialization."""

    def test_audit_record_creation_with_defaults(self):
        """Test creating AuditRecord with default values."""
        record = AuditRecord()
        assert record.surface_id == ""
        assert record.mode == AutonomyMode.SAFE_AUTO
        assert record.actor == ""
        assert record.decision == "allow"
        assert record.runner_class == "hosted"
        assert record.mutation_class == "READ_ONLY"

    def test_audit_record_creation_with_values(self):
        """Test creating AuditRecord with explicit values."""
        record = AuditRecord(
            surface_id="AUT-001",
            mode=AutonomyMode.SAFE_AUTO,
            actor="testuser",
            event_type="issue_comment",
            token_source="github_app",
            runner_class="hosted",
            mutation_class="ADVISORY_WRITE",
            prompt_id="test-prompt",
            decision="allow",
            policy_reason="test_allowed",
            target="PR#1234",
            run_id="run-001",
        )
        assert record.surface_id == "AUT-001"
        assert record.actor == "testuser"
        assert record.event_type == "issue_comment"
        assert record.token_source == "github_app"
        assert record.mutation_class == "ADVISORY_WRITE"
        assert record.prompt_id == "test-prompt"
        assert record.target == "PR#1234"
        assert record.run_id == "run-001"

    def test_audit_record_auto_timestamp(self):
        """Test that timestamp is auto-generated."""
        before = time.time()
        record = AuditRecord()
        after = time.time()
        assert before <= record.ts <= after

    def test_audit_record_auto_record_id(self):
        """Test that record_id is auto-generated."""
        record = AuditRecord()
        assert record.record_id is not None
        assert len(record.record_id) == 8  # UUID truncated to 8 chars
        assert record.record_id.isalnum() or "-" in record.record_id

    def test_audit_record_to_dict(self):
        """Test converting AuditRecord to dictionary."""
        record = AuditRecord(
            surface_id="AUT-001",
            actor="testuser",
            decision="deny",
            policy_reason="not_allowed",
        )
        record_dict = record.to_dict()
        assert isinstance(record_dict, dict)
        assert record_dict["surface_id"] == "AUT-001"
        assert record_dict["actor"] == "testuser"
        assert record_dict["decision"] == "deny"
        assert record_dict["policy_reason"] == "not_allowed"
        assert "ts" in record_dict
        assert "record_id" in record_dict

    def test_audit_record_to_dict_mode_enum_conversion(self):
        """Test that AutonomyMode enum is properly converted to string in dict."""
        record = AuditRecord(mode=AutonomyMode.SAFE_AUTO)
        record_dict = record.to_dict()
        assert isinstance(record_dict["mode"], str)
        assert record_dict["mode"] == AutonomyMode.SAFE_AUTO.value

    def test_audit_record_to_dict_string_mode(self):
        """Test to_dict when mode is already a string."""
        record = AuditRecord()
        record.mode = "custom_mode"  # Set as string instead of enum
        record_dict = record.to_dict()
        assert record_dict["mode"] == "custom_mode"

    def test_audit_record_all_fields_in_dict(self):
        """Test that all fields are present in dictionary output."""
        record = AuditRecord(
            surface_id="S1",
            actor="A1",
            event_type="E1",
            token_source="T1",
            runner_class="R1",
            mutation_class="M1",
            prompt_id="P1",
            decision="D1",
            policy_reason="PR1",
            target="TG1",
            run_id="RU1",
        )
        record_dict = record.to_dict()
        expected_fields = {
            "ts",
            "record_id",
            "surface_id",
            "mode",
            "actor",
            "event_type",
            "token_source",
            "runner_class",
            "mutation_class",
            "prompt_id",
            "decision",
            "policy_reason",
            "target",
            "run_id",
        }
        assert set(record_dict.keys()) == expected_fields

    def test_audit_record_decision_values(self):
        """Test AuditRecord with different decision values."""
        for decision in ["allow", "deny", "dry_run"]:
            record = AuditRecord(decision=decision)
            assert record.decision == decision


class TestMetricsSnapshot:
    """Test MetricsSnapshot dataclass for metric aggregation."""

    def test_metrics_snapshot_creation(self):
        """Test creating MetricsSnapshot with default values."""
        metrics = MetricsSnapshot()
        assert metrics.total_records == 0
        assert metrics.dry_run_count == 0
        assert metrics.approval_bypass_attempts == 0
        assert len(metrics.autonomy_mode_count) == 0

    def test_metrics_snapshot_dry_run_ratio_zero(self):
        """Test dry_run_ratio when total_records is 0."""
        metrics = MetricsSnapshot()
        assert metrics.dry_run_ratio == 0.0

    def test_metrics_snapshot_dry_run_ratio_calculation(self):
        """Test dry_run_ratio calculation."""
        metrics = MetricsSnapshot()
        metrics.total_records = 10
        metrics.dry_run_count = 3
        assert metrics.dry_run_ratio == pytest.approx(0.3)

    def test_metrics_snapshot_dry_run_ratio_full(self):
        """Test dry_run_ratio when all records are dry runs."""
        metrics = MetricsSnapshot()
        metrics.total_records = 5
        metrics.dry_run_count = 5
        assert metrics.dry_run_ratio == pytest.approx(1.0)

    def test_metrics_snapshot_counter_updates(self):
        """Test updating various counters in MetricsSnapshot."""
        metrics = MetricsSnapshot()
        metrics.total_records = 5
        metrics.autonomy_mode_count["SAFE_AUTO"] = 3
        metrics.autonomy_mode_count["FULL_AUTO"] = 2
        metrics.mutation_count_by_class["READ_ONLY"] = 4
        metrics.mutation_count_by_class["WRITE"] = 1

        assert metrics.total_records == 5
        assert metrics.autonomy_mode_count["SAFE_AUTO"] == 3
        assert metrics.autonomy_mode_count["FULL_AUTO"] == 2
        assert metrics.mutation_count_by_class["READ_ONLY"] == 4

    def test_metrics_snapshot_to_dict(self):
        """Test converting MetricsSnapshot to dictionary."""
        metrics = MetricsSnapshot()
        metrics.total_records = 10
        metrics.dry_run_count = 2
        metrics.autonomy_mode_count["SAFE_AUTO"] = 10

        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert metrics_dict["total_records"] == 10
        assert metrics_dict["dry_run_count"] == 2
        assert metrics_dict["dry_run_ratio"] == pytest.approx(0.2)
        assert "ts" in metrics_dict

    def test_metrics_snapshot_dict_contains_all_fields(self):
        """Test that all metric fields are in dictionary output."""
        metrics = MetricsSnapshot()
        metrics_dict = metrics.to_dict()
        expected_fields = {
            "ts",
            "total_records",
            "dry_run_ratio",
            "approval_bypass_attempts",
            "autonomy_mode_count",
            "surface_invocation_count",
            "mutation_count_by_class",
            "token_source_count",
            "runner_class_count",
            "deny_count_by_policy",
            "dispatch_event_count",
            "prompt_family_count",
        }
        assert set(metrics_dict.keys()) == expected_fields


class TestAuditLogger:
    """Test AuditLogger for recording and flushing audit records."""

    @pytest.fixture
    def temp_audit_dir(self):
        """Create temporary directory for audit logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def audit_logger(self, temp_audit_dir):
        """Create AuditLogger instance with temporary paths."""
        audit_path = temp_audit_dir / "audit.ndjson"
        metrics_path = temp_audit_dir / "metrics.ndjson"
        with patch("codex.autonomy.audit.AutonomyRegistry.load"):
            logger = AuditLogger(audit_path=audit_path, metrics_path=metrics_path)
        return logger

    def test_audit_logger_initialization(self, audit_logger):
        """Test AuditLogger initialization."""
        assert audit_logger._audit_path is not None
        assert audit_logger._metrics_path is not None
        assert audit_logger._metrics is not None
        assert isinstance(audit_logger._metrics, MetricsSnapshot)

    def test_audit_logger_default_factory(self):
        """Test AuditLogger.default() class method."""
        with patch("codex.autonomy.audit.AutonomyRegistry.load"):
            logger = AuditLogger.default()
        assert isinstance(logger, AuditLogger)

    def test_audit_logger_record_single(self, audit_logger, temp_audit_dir):
        """Test recording a single audit record."""
        record = AuditRecord(
            surface_id="AUT-001",
            actor="testuser",
            decision="allow",
        )
        audit_logger.record(record)

        assert audit_logger._metrics.total_records == 1
        assert audit_logger._metrics.autonomy_mode_count["SAFE_AUTO"] == 1

    def test_audit_logger_record_multiple(self, audit_logger):
        """Test recording multiple audit records."""
        records = [
            AuditRecord(surface_id="AUT-001", actor="user1"),
            AuditRecord(surface_id="AUT-002", actor="user2"),
            AuditRecord(surface_id="AUT-001", actor="user3"),
        ]
        for record in records:
            audit_logger.record(record)

        assert audit_logger._metrics.total_records == 3
        assert audit_logger._metrics.surface_invocation_count["AUT-001"] == 2
        assert audit_logger._metrics.surface_invocation_count["AUT-002"] == 1

    def test_audit_logger_record_updates_metrics(self, audit_logger):
        """Test that record() updates all relevant metrics."""
        record = AuditRecord(
            surface_id="AUT-001",
            mutation_class="WRITE",
            token_source="github_app",
            runner_class="container",
            event_type="pull_request",
            prompt_id="test-prompt",
            decision="deny",
            policy_reason="unauthorized",
        )
        audit_logger.record(record)

        metrics = audit_logger._metrics
        assert metrics.total_records == 1
        assert metrics.surface_invocation_count["AUT-001"] == 1
        assert metrics.mutation_count_by_class["WRITE"] == 1
        assert metrics.token_source_count["github_app"] == 1
        assert metrics.runner_class_count["container"] == 1
        assert metrics.dispatch_event_count["pull_request"] == 1
        assert metrics.prompt_family_count["test-prompt"] == 1
        assert metrics.deny_count_by_policy["unauthorized"] == 1

    def test_audit_logger_record_dry_run(self, audit_logger):
        """Test recording dry_run decision."""
        record = AuditRecord(decision="dry_run")
        audit_logger.record(record)

        assert audit_logger._metrics.dry_run_count == 1

    def test_audit_logger_record_multiple_dry_runs(self, audit_logger):
        """Test recording multiple dry_run decisions."""
        for _ in range(5):
            record = AuditRecord(decision="dry_run")
            audit_logger.record(record)

        assert audit_logger._metrics.total_records == 5
        assert audit_logger._metrics.dry_run_count == 5
        assert audit_logger._metrics.dry_run_ratio == pytest.approx(1.0)

    def test_audit_logger_record_deny_truncates_reason(self, audit_logger):
        """Test that deny policy reason is truncated to 40 chars."""
        long_reason = "a" * 100
        record = AuditRecord(decision="deny", policy_reason=long_reason)
        audit_logger.record(record)

        metrics = audit_logger._metrics
        deny_keys = list(metrics.deny_count_by_policy.keys())
        assert len(deny_keys) == 1
        assert len(deny_keys[0]) == 40

    def test_audit_logger_metrics_property(self, audit_logger):
        """Test accessing metrics property."""
        record = AuditRecord()
        audit_logger.record(record)

        metrics = audit_logger.metrics
        assert isinstance(metrics, MetricsSnapshot)
        assert metrics.total_records == 1

    def test_audit_logger_audit_coverage_zero(self, audit_logger):
        """Test audit_coverage when no records."""
        coverage = audit_logger.audit_coverage(100)
        assert coverage == 0.0

    def test_audit_logger_audit_coverage_full(self, audit_logger):
        """Test audit_coverage when all runs recorded."""
        for _ in range(10):
            audit_logger.record(AuditRecord())

        coverage = audit_logger.audit_coverage(10)
        assert coverage == pytest.approx(1.0)

    def test_audit_logger_audit_coverage_partial(self, audit_logger):
        """Test audit_coverage with partial coverage."""
        for _ in range(25):
            audit_logger.record(AuditRecord())

        coverage = audit_logger.audit_coverage(100)
        assert coverage == pytest.approx(0.25)

    def test_audit_logger_audit_coverage_capped_at_one(self, audit_logger):
        """Test that audit_coverage is capped at 1.0."""
        for _ in range(20):
            audit_logger.record(AuditRecord())

        coverage = audit_logger.audit_coverage(10)
        assert coverage == pytest.approx(1.0)

    def test_audit_logger_audit_coverage_zero_total_runs(self, audit_logger):
        """Test audit_coverage with zero total_runs."""
        coverage = audit_logger.audit_coverage(0)
        assert coverage == 0.0

    def test_audit_logger_audit_coverage_negative_total_runs(self, audit_logger):
        """Test audit_coverage with negative total_runs."""
        coverage = audit_logger.audit_coverage(-1)
        assert coverage == 0.0

    def test_audit_logger_flush_metrics_writes_file(self, audit_logger, temp_audit_dir):
        """Test that flush_metrics writes to metrics file."""
        for _ in range(3):
            audit_logger.record(AuditRecord())

        audit_logger.flush_metrics()

        metrics_file = temp_audit_dir / "metrics.ndjson"
        assert metrics_file.exists()

        # Read and verify content
        with open(metrics_file) as f:
            line = f.readline().strip()
            data = json.loads(line)
            assert data["total_records"] == 3

    @patch("codex.autonomy.audit.logger")
    def test_audit_logger_flush_metrics_logs(self, mock_logger, audit_logger):
        """Test that flush_metrics logs info message."""
        for _ in range(5):
            audit_logger.record(AuditRecord())

        audit_logger.flush_metrics()

        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args
        assert "flushed metrics" in call_args[0][0]
        assert call_args[0][1] == 5  # total_records

    def test_audit_logger_record_empty_optional_fields(self, audit_logger):
        """Test recording when optional fields are empty."""
        record = AuditRecord(
            surface_id="",
            token_source="",
            runner_class="",
            event_type="",
            prompt_id="",
            policy_reason="",
        )
        audit_logger.record(record)

        metrics = audit_logger._metrics
        assert len(metrics.surface_invocation_count) == 0
        assert len(metrics.token_source_count) == 0
        assert len(metrics.runner_class_count) == 0
        assert len(metrics.dispatch_event_count) == 0
        assert len(metrics.prompt_family_count) == 0
        assert metrics.total_records == 1

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.open")
    def test_audit_logger_write_ndjson_creates_parent(self, mock_open, mock_mkdir):
        """Test that _write_ndjson creates parent directories."""
        path = Path("/test/audit.ndjson")
        data = {"test": "data"}

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        AuditLogger._write_ndjson(path, data)

        mock_mkdir.assert_called_once()
        mock_file.write.assert_called_once()

    @patch("pathlib.Path.open", side_effect=OSError("Permission denied"))
    @patch("codex.autonomy.audit.logger")
    def test_audit_logger_write_ndjson_handles_error(self, mock_logger, mock_open):
        """Test that _write_ndjson handles OSError gracefully."""
        path = Path("/test/audit.ndjson")
        data = {"test": "data"}

        AuditLogger._write_ndjson(path, data)

        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args
        assert "failed to write" in call_args[0][0]


class TestAuditLoggerIntegration:
    """Integration tests for the full audit logging workflow."""

    @pytest.fixture
    def temp_audit_dir(self):
        """Create temporary directory for audit logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def audit_logger(self, temp_audit_dir):
        """Create AuditLogger instance with temporary paths."""
        audit_path = temp_audit_dir / "audit.ndjson"
        metrics_path = temp_audit_dir / "metrics.ndjson"
        with patch("codex.autonomy.audit.AutonomyRegistry.load"):
            logger = AuditLogger(audit_path=audit_path, metrics_path=metrics_path)
        return logger

    def test_end_to_end_record_and_flush(self, audit_logger, temp_audit_dir):
        """Test end-to-end workflow of recording and flushing."""
        # Record multiple decisions
        records = [
            AuditRecord(
                surface_id="AUT-001",
                actor="user1",
                decision="allow",
                mutation_class="READ_ONLY",
            ),
            AuditRecord(
                surface_id="AUT-002",
                actor="user2",
                decision="deny",
                mutation_class="WRITE",
            ),
            AuditRecord(
                surface_id="AUT-001",
                actor="user1",
                decision="dry_run",
                mutation_class="READ_ONLY",
            ),
        ]

        for record in records:
            audit_logger.record(record)

        # Verify metrics before flush
        assert audit_logger._metrics.total_records == 3
        assert audit_logger._metrics.dry_run_count == 1
        assert audit_logger._metrics.dry_run_ratio == pytest.approx(1 / 3)

        # Flush metrics
        audit_logger.flush_metrics()

        # Verify files exist
        audit_file = temp_audit_dir / "audit.ndjson"
        metrics_file = temp_audit_dir / "metrics.ndjson"
        assert audit_file.exists()
        assert metrics_file.exists()
