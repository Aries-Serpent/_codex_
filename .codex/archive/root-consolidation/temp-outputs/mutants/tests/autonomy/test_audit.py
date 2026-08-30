"""
Tests for Phase 5 — Audit / Observability Plane
(src/codex/autonomy/audit.py)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.autonomy.audit import AuditLogger, AuditRecord, MetricsSnapshot
from codex.autonomy.registry import AutonomyMode, AutonomyRegistry


def _logger(tmp_path: Path) -> AuditLogger:
    reg = AutonomyRegistry(
        audit_log_path=str(tmp_path / "audit.ndjson"),
        metrics_log_path=str(tmp_path / "metrics.ndjson"),
    )
    return AuditLogger(registry=reg)


class TestAuditRecord:
    def test_to_dict_contains_required_fields(self):
        rec = AuditRecord(
            surface_id="AUT-007",
            mode=AutonomyMode.SAFE_AUTO,
            actor="mbaetiong",
            event_type="issue_comment",
            token_source="github_app",
            runner_class="hosted",
            mutation_class="ADVISORY_WRITE",
            prompt_id="system-copilot-agent",
            decision="allow",
            policy_reason="allowed",
            target="PR#4254",
            run_id="25329390481",
        )
        d = rec.to_dict()
        required = {
            "ts",
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
        assert required.issubset(d.keys()), "Condition must be true"

    def test_mode_serialised_as_string(self):
        rec = AuditRecord(mode=AutonomyMode.DRY_RUN)
        assert rec.to_dict()["mode"] == "DRY_RUN", "Condition must be true"

    def test_record_id_auto_generated(self):
        r1 = AuditRecord()
        r2 = AuditRecord()
        assert r1.record_id != r2.record_id, "record_id is not valid"


class TestAuditLogger:
    def test_record_writes_ndjson(self, tmp_path):
        al = _logger(tmp_path)
        al.record(AuditRecord(surface_id="AUT-007", decision="allow"))
        lines = (tmp_path / "audit.ndjson").read_text().strip().splitlines()
        assert len(lines) == 1, "Lines must not be empty"
        data = json.loads(lines[0])
        assert data["surface_id"] == "AUT-007", "Data must not be empty"
        assert data["decision"] == "allow", "Data must not be empty"

    def test_multiple_records_appended(self, tmp_path):
        al = _logger(tmp_path)
        for i in range(3):
            al.record(AuditRecord(surface_id=f"AUT-{i:03d}"))
        lines = (tmp_path / "audit.ndjson").read_text().strip().splitlines()
        assert len(lines) == 3, "Lines must not be empty"

    def test_metrics_update_on_record(self, tmp_path):
        al = _logger(tmp_path)
        al.record(
            AuditRecord(
                surface_id="AUT-007",
                mode=AutonomyMode.SAFE_AUTO,
                decision="allow",
                mutation_class="ADVISORY_WRITE",
            )
        )
        m = al.metrics
        assert m.total_records == 1, "total_records is not valid"
        assert m.surface_invocation_count["AUT-007"] == 1, "Count must be greater than zero"
        assert m.mutation_count_by_class["ADVISORY_WRITE"] == 1, "Count must be greater than zero"
        assert m.autonomy_mode_count["SAFE_AUTO"] == 1, "Count must be greater than zero"

    def test_deny_increments_deny_count(self, tmp_path):
        al = _logger(tmp_path)
        al.record(AuditRecord(decision="deny", policy_reason="kill_switch=true"))
        assert al.metrics.deny_count_by_policy, "Count must be greater than zero"

    def test_dry_run_increments_dry_run_count(self, tmp_path):
        al = _logger(tmp_path)
        al.record(AuditRecord(decision="dry_run"))
        assert al.metrics.dry_run_count == 1, "Count must be greater than zero"

    def test_dry_run_ratio(self, tmp_path):
        al = _logger(tmp_path)
        al.record(AuditRecord(decision="allow"))
        al.record(AuditRecord(decision="dry_run"))
        assert al.metrics.dry_run_ratio == pytest.approx(0.5), "dry_run_ratio is not valid"

    def test_flush_metrics_writes_file(self, tmp_path):
        al = _logger(tmp_path)
        al.record(AuditRecord(surface_id="AUT-009"))
        al.flush_metrics()
        lines = (tmp_path / "metrics.ndjson").read_text().strip().splitlines()
        assert len(lines) == 1, "Lines must not be empty"
        data = json.loads(lines[0])
        assert data["total_records"] == 1, "Data must not be empty"

    def test_audit_coverage_zero_when_no_runs(self, tmp_path):
        al = _logger(tmp_path)
        assert al.audit_coverage(total_runs=0) == 0.0, "Condition must be true"

    def test_audit_coverage_capped_at_one(self, tmp_path):
        al = _logger(tmp_path)
        al.record(AuditRecord())
        al.record(AuditRecord())
        assert al.audit_coverage(total_runs=1) == 1.0, "Condition must be true"

    def test_audit_coverage_partial(self, tmp_path):
        al = _logger(tmp_path)
        for _ in range(8):
            al.record(AuditRecord())
        assert al.audit_coverage(total_runs=10) == pytest.approx(0.8), "Condition must be true"

    def test_write_failure_does_not_raise(self, tmp_path):
        # Point audit path to a directory (unwriteable as file)
        bad_path = tmp_path / "audit.ndjson"
        bad_path.mkdir()
        reg = AutonomyRegistry(
            audit_log_path=str(bad_path),
            metrics_log_path=str(tmp_path / "metrics.ndjson"),
        )
        al = AuditLogger(registry=reg)
        al.record(AuditRecord())  # should not raise


class TestMetricsSnapshot:
    def test_dry_run_ratio_zero_no_records(self):
        m = MetricsSnapshot()
        assert m.dry_run_ratio == 0.0, "dry_run_ratio is not valid"

    def test_to_dict_contains_all_metrics(self):
        m = MetricsSnapshot(total_records=5, dry_run_count=1)
        d = m.to_dict()
        assert d["total_records"] == 5, "Condition must be true"
        assert d["dry_run_ratio"] == pytest.approx(0.2), "Condition must be true"
        assert "ts" in d, "Condition must be true"
