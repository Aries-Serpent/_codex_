"""Tests for Skills telemetry module."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from codex.skills.models import BudgetUsed, ExecutionMetrics
from codex.skills.telemetry import (
    emit_event,
    read_events,
    skill_invocation_span,
    summarise_events,
)


@pytest.fixture
def telemetry_path(tmp_path):
    log_file = tmp_path / "skill_events.jsonl"
    os.environ["CODEX_SKILL_TELEMETRY_PATH"] = str(log_file)
    yield log_file
    del os.environ["CODEX_SKILL_TELEMETRY_PATH"]


@pytest.fixture
def sample_metrics():
    return ExecutionMetrics(
        latency_ms=123,
        budget_used=BudgetUsed(calls=1, tokens=500, wallclock_ms=123),
        aais_score=0.88,
        compression_ratio=0.42,
    )


class TestEmitEvent:
    def test_emit_jsonl_writes_record(self, telemetry_path, sample_metrics):
        emit_event(
            skill_id="doc.retriever.core",
            version="1.0.0",
            status="ok",
            metrics=sample_metrics,
            trace_id="test-trace-001",
            emit_jsonl=True,
            emit_otel=False,
        )
        assert telemetry_path.exists(), "Condition must be true"
        lines = telemetry_path.read_text().strip().split("\n")
        assert len(lines) == 1, "Lines must not be empty"
        record = json.loads(lines[0])
        assert record["skill_id"] == "doc.retriever.core", "rec is not valid"
        assert record["status"] == "ok", "rec is not valid"
        assert record["latency_ms"] == 123, "rec is not valid"
        assert record["trace_id"] == "test-trace-001", "rec is not valid"

    def test_emit_no_jsonl_does_not_write(self, telemetry_path, sample_metrics):
        emit_event(
            skill_id="test.skill",
            version="1.0.0",
            status="ok",
            metrics=sample_metrics,
            trace_id="t1",
            emit_jsonl=False,
            emit_otel=False,
        )
        assert not telemetry_path.exists(), "Condition must be true"

    def test_emit_returns_telemetry_event(self, telemetry_path, sample_metrics):
        from codex.skills.models import TelemetryEvent

        event = emit_event(
            skill_id="test.skill",
            version="1.0.0",
            status="error",
            metrics=sample_metrics,
            trace_id="t2",
            emit_jsonl=True,
        )
        assert isinstance(event, TelemetryEvent)
        assert event.status == "error", "Error should be raised or set"

    def test_multiple_events_append(self, telemetry_path, sample_metrics):
        for i in range(3):
            emit_event(
                skill_id=f"skill.{i}",
                version="1.0.0",
                status="ok",
                metrics=sample_metrics,
                trace_id=f"trace-{i}",
                emit_jsonl=True,
            )
        lines = telemetry_path.read_text().strip().split("\n")
        assert len(lines) == 3, "Lines must not be empty"


class TestReadEvents:
    def test_read_events_from_file(self, telemetry_path, sample_metrics):
        emit_event(
            skill_id="s1",
            version="1.0.0",
            status="ok",
            metrics=sample_metrics,
            trace_id="t1",
            emit_jsonl=True,
        )
        events = read_events(telemetry_path)
        assert len(events) == 1, "Events must not be empty"
        assert events[0].skill_id == "s1", "skill_id is not valid"

    def test_read_events_empty_file_returns_empty(self, tmp_path):
        log = tmp_path / "empty.jsonl"
        log.write_text("")
        assert read_events(log) == [], "Condition must be true"

    def test_read_events_missing_file_returns_empty(self, tmp_path):
        assert read_events(tmp_path / "nonexistent.jsonl") == [], "Condition must be true"

    def test_read_events_skips_malformed_lines(self, telemetry_path, sample_metrics):
        emit_event(
            skill_id="s1",
            version="1.0.0",
            status="ok",
            metrics=sample_metrics,
            trace_id="t1",
            emit_jsonl=True,
        )
        telemetry_path.write_text(telemetry_path.read_text() + "not valid json\n")
        events = read_events(telemetry_path)
        assert len(events) == 1, "Events must not be empty"


class TestSummariseEvents:
    def test_summary_counts(self, telemetry_path, sample_metrics):
        for status in ["ok", "ok", "error"]:
            emit_event(
                skill_id="s1",
                version="1.0.0",
                status=status,
                metrics=sample_metrics,
                trace_id="t",
                emit_jsonl=True,
            )
        events = read_events(telemetry_path)
        summary = summarise_events(events)
        assert summary["total"] == 3, "Condition must be true"
        assert summary["ok"] == 2, "Condition must be true"
        assert summary["error"] == 1, "Error should be raised or set"

    def test_summary_avg_latency(self, telemetry_path):
        metrics_100 = ExecutionMetrics(latency_ms=100, budget_used=BudgetUsed())
        metrics_200 = ExecutionMetrics(latency_ms=200, budget_used=BudgetUsed())
        emit_event(
            skill_id="s",
            version="1.0.0",
            status="ok",
            metrics=metrics_100,
            trace_id="t1",
            emit_jsonl=True,
        )
        emit_event(
            skill_id="s",
            version="1.0.0",
            status="ok",
            metrics=metrics_200,
            trace_id="t2",
            emit_jsonl=True,
        )
        events = read_events(telemetry_path)
        summary = summarise_events(events)
        assert summary["avg_latency_ms"] == 150.0, "Condition must be true"

    def test_summary_empty_events(self):
        summary = summarise_events([])
        assert summary["total"] == 0, "Condition must be true"
        assert summary["avg_latency_ms"] == 0, "Condition must be true"


class TestSkillInvocationSpan:
    def test_span_no_otel_yields_none(self):
        with patch("importlib.util.find_spec", return_value=None):
            with skill_invocation_span("test.skill") as span:
                assert span is None, "span is not valid"

    def test_span_context_manager_runs_body(self):
        executed = []
        with patch("importlib.util.find_spec", return_value=None):
            with skill_invocation_span("test.skill", capability_tags=["test"]):
                executed.append(True)
        assert executed == [True], "executed is not valid"

    def test_span_propagates_exceptions(self):
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(RuntimeError, match="test error"):
                with skill_invocation_span("test.skill"):
                    raise RuntimeError("test error")
