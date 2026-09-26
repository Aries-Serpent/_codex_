"""Tests for decision forensics — TelemetryEvent Phase 2 fields.

Covers:
- Unit: TelemetryEvent has decision_id, turn_id, task_id fields
- Unit: forensics() emit method creates event with correct payload
- Unit: NDJSON backend backward-compat with old records lacking new fields
- Unit: orchestration events include forensics event from kernel.plan_tools
- Integration: kernel.plan_tools emits forensics event
- Integration: forensics event has selected_toolchain and rejected_alternatives
"""

from __future__ import annotations

import json
from pathlib import Path

from codex.cognitive_brain.kernel import CognitiveBrainKernel, KernelConfig, reset_kernel
from codex.cognitive_brain.telemetry import (
    CognitiveTelemetry,
    InMemoryTelemetryBackend,
    NDJSONTelemetryBackend,
    TelemetryEvent,
)

# ---------------------------------------------------------------------------
# TelemetryEvent Phase 2 fields
# ---------------------------------------------------------------------------


class TestTelemetryEventForensicsFields:
    def test_telemetry_event_has_decision_id(self) -> None:
        event = TelemetryEvent(event_type="test", decision_id="d-001")
        assert event.decision_id == "d-001", "decision_id is not valid"

    def test_telemetry_event_has_turn_id(self) -> None:
        event = TelemetryEvent(event_type="test", turn_id="t-42")
        assert event.turn_id == "t-42", "turn_id is not valid"

    def test_telemetry_event_has_task_id(self) -> None:
        event = TelemetryEvent(event_type="test", task_id="task-99")
        assert event.task_id == "task-99", "task_id is not valid"

    def test_defaults_are_none(self) -> None:
        event = TelemetryEvent(event_type="test")
        assert event.decision_id is None, "decision_id is not valid"
        assert event.turn_id is None, "turn_id is not valid"
        assert event.task_id is None, "task_id is not valid"

    def test_to_dict_includes_forensics_fields(self) -> None:
        event = TelemetryEvent(
            event_type="forensics",
            decision_id="d-001",
            turn_id="t-1",
            task_id="task-5",
        )
        data = event.to_dict()
        assert data["decision_id"] == "d-001", "Data must not be empty"
        assert data["turn_id"] == "t-1", "Data must not be empty"
        assert data["task_id"] == "task-5", "Data must not be empty"

    def test_to_json_includes_forensics_fields(self) -> None:
        event = TelemetryEvent(
            event_type="forensics",
            decision_id="d-007",
            turn_id="t-7",
        )
        payload = json.loads(event.to_json())
        assert payload["decision_id"] == "d-007", "Condition must be true"
        assert payload["turn_id"] == "t-7", "Condition must be true"


# ---------------------------------------------------------------------------
# CognitiveTelemetry.forensics() emit method
# ---------------------------------------------------------------------------


class TestForensicsEmit:
    def test_forensics_emits_event(self) -> None:
        backend = InMemoryTelemetryBackend()
        tel = CognitiveTelemetry(backends=[backend])
        tel.forensics(
            decision_id="d-123",
            turn_id="t-5",
            task_id="task-10",
            selected_toolchain="github_mcp",
            rejected_alternatives=["playwright", "web_search"],
            negotiation_outcome="No fallback needed",
        )
        events = tel.query(event_type="forensics")
        assert len(events) == 1, "Events must not be empty"

    def test_forensics_event_has_decision_id(self) -> None:
        backend = InMemoryTelemetryBackend()
        tel = CognitiveTelemetry(backends=[backend])
        tel.forensics(
            decision_id="d-abc",
            turn_id=None,
            task_id=None,
            selected_toolchain="playwright",
            rejected_alternatives=[],
            negotiation_outcome=None,
        )
        events = tel.query(event_type="forensics")
        assert events[0].decision_id == "d-abc", "decision_id is not valid"

    def test_forensics_event_payload_selected_toolchain(self) -> None:
        backend = InMemoryTelemetryBackend()
        tel = CognitiveTelemetry(backends=[backend])
        tel.forensics(
            decision_id="d-xyz",
            turn_id="t-1",
            task_id="t-1",
            selected_toolchain="shell",
            rejected_alternatives=["github_mcp"],
            negotiation_outcome="shell policy allowed",
        )
        event = tel.query(event_type="forensics")[0]
        assert event.payload["selected_toolchain"] == "shell", "Condition must be true"
        assert "github_mcp" in event.payload["rejected_alternatives"], "Condition must be true"

    def test_forensics_event_extra_payload(self) -> None:
        backend = InMemoryTelemetryBackend()
        tel = CognitiveTelemetry(backends=[backend])
        tel.forensics(
            decision_id="d-extra",
            turn_id=None,
            task_id=None,
            selected_toolchain="github_mcp",
            rejected_alternatives=[],
            negotiation_outcome=None,
            extra={"custom_key": "custom_value"},
        )
        event = tel.query(event_type="forensics")[0]
        assert event.payload.get("custom_key") == "custom_value", "Value must be initialized"


# ---------------------------------------------------------------------------
# NDJSON backward-compat (old records without new fields)
# ---------------------------------------------------------------------------


class TestNDJSONBackwardCompat:
    def test_old_record_without_decision_id_loaded(self, tmp_path: Path) -> None:
        """Records written before Phase 2 must load without KeyError."""
        ndjson_path = tmp_path / "telemetry.ndjson"
        # Write an old-style record without forensics fields.
        old_record = {
            "event_type": "negotiation",
            "timestamp": "2026-01-01T00:00:00Z",
            "model_id": "claude-haiku-4.5",
            "payload": {"stripped_params": ["reasoning_effort"]},
            "notes": [],
        }
        ndjson_path.write_text(json.dumps(old_record) + "\n")
        backend = NDJSONTelemetryBackend(ndjson_path)
        events = backend.read_all()
        assert len(events) == 1, "Events must not be empty"
        assert events[0].event_type == "negotiation", "event_type is not valid"
        # New fields must default to None (not raise).
        assert events[0].decision_id is None, "decision_id is not valid"
        assert events[0].turn_id is None, "turn_id is not valid"
        assert events[0].task_id is None, "task_id is not valid"

    def test_record_with_unknown_field_loaded(self, tmp_path: Path) -> None:
        """Records with extra future fields must not cause errors."""
        ndjson_path = tmp_path / "telemetry.ndjson"
        future_record = {
            "event_type": "startup",
            "timestamp": "2026-01-01T00:00:00Z",
            "payload": {},
            "notes": [],
            "future_unknown_field": "value_from_future",
        }
        ndjson_path.write_text(json.dumps(future_record) + "\n")
        backend = NDJSONTelemetryBackend(ndjson_path)
        events = backend.read_all()
        assert len(events) == 1, "Events must not be empty"
        assert events[0].event_type == "startup", "event_type is not valid"


# ---------------------------------------------------------------------------
# Kernel plan_tools emits forensics event
# ---------------------------------------------------------------------------


class TestKernelPlanToolsForensics:
    def setup_method(self) -> None:
        reset_kernel()

    def teardown_method(self) -> None:
        reset_kernel()

    def _fresh_kernel(self) -> CognitiveBrainKernel:
        k = CognitiveBrainKernel(config=KernelConfig())
        k.boot()
        return k

    def test_plan_tools_emits_forensics_event(self) -> None:
        k = self._fresh_kernel()
        k.plan_tools("repo_introspection")
        events = k.telemetry.query(event_type="forensics")
        assert len(events) >= 1, "Events must not be empty"

    def test_forensics_event_has_decision_id(self) -> None:
        k = self._fresh_kernel()
        k.plan_tools("repo_introspection")
        events = k.telemetry.query(event_type="forensics")
        assert events[-1].decision_id is not None, "decision_id must be initialized"

    def test_forensics_event_selected_toolchain(self) -> None:
        k = self._fresh_kernel()
        k.plan_tools("repo_introspection")
        events = k.telemetry.query(event_type="forensics")
        payload = events[-1].payload
        assert "selected_toolchain" in payload, "Condition must be true"
        assert payload["selected_toolchain"] == "github_mcp", "Condition must be true"

    def test_forensics_event_with_turn_id(self) -> None:
        k = self._fresh_kernel()
        k.plan_tools("code_search", turn_id="t-001", task_id="pr-42")
        events = k.telemetry.query(event_type="forensics")
        last = events[-1]
        assert last.turn_id == "t-001", "turn_id is not valid"
        assert last.task_id == "pr-42", "task_id is not valid"

    def test_forensics_event_rejected_alternatives_present(self) -> None:
        k = self._fresh_kernel()
        k.plan_tools("repo_introspection")
        events = k.telemetry.query(event_type="forensics")
        payload = events[-1].payload
        assert "rejected_alternatives" in payload, "Condition must be true"
