"""Tests for src/codex/cognitive/safety_guards.py — Phase 10B coverage.

Covers AuditEventType, OverrideType, AuditEvent, RollbackRecord,
RateLimit, ScopeRestriction, AuditLog, and SafetyGuard.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType
from codex.cognitive.safety_guards import (
    AuditEvent,
    AuditEventType,
    AuditLog,
    OverrideType,
    RateLimit,
    RollbackRecord,
    SafetyGuard,
    ScopeRestriction,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_audit_event_types(self):
        assert AuditEventType.ADJUSTMENT_PROPOSED.value == "adjustment_proposed"
        assert AuditEventType.RATE_LIMIT_HIT.value == "rate_limit_hit"
        assert AuditEventType.SCOPE_VIOLATION.value == "scope_violation"

    def test_override_types(self):
        assert OverrideType.PAUSE_AUTOMATION.value == "pause_automation"
        assert OverrideType.BLOCK_RULE.value == "block_rule"


# ---------------------------------------------------------------------------
# AuditEvent
# ---------------------------------------------------------------------------

class TestAuditEvent:
    def test_roundtrip(self):
        now = datetime.now(timezone.utc)
        event = AuditEvent(
            id="AUD-000001",
            event_type=AuditEventType.ADJUSTMENT_PROPOSED,
            timestamp=now,
            actor="system",
            details={"rule_id": "R1"},
            context={"session": "S1"},
        )
        d = event.to_dict()
        restored = AuditEvent.from_dict(d)
        assert restored.id == event.id
        assert restored.event_type == event.event_type
        assert restored.actor == "system"

    def test_default_context(self):
        d = {
            "id": "AUD-000001",
            "event_type": "adjustment_proposed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": "test",
            "details": {},
        }
        event = AuditEvent.from_dict(d)
        assert event.context == {}


# ---------------------------------------------------------------------------
# RollbackRecord
# ---------------------------------------------------------------------------

class TestRollbackRecord:
    def test_to_dict(self):
        now = datetime.now(timezone.utc)
        rec = RollbackRecord(
            id="RB-001",
            original_adjustment_id="ADJ-001",
            original_state={"priority": 1},
            rolled_back_at=now,
            rolled_back_by="admin",
            reason="Wrong priority",
        )
        d = rec.to_dict()
        assert d["id"] == "RB-001"
        assert d["reason"] == "Wrong priority"


# ---------------------------------------------------------------------------
# RateLimit
# ---------------------------------------------------------------------------

class TestRateLimit:
    def test_allows_within_limit(self):
        rl = RateLimit("test_action", max_count=3, window_hours=1)
        allowed, msg = rl.check_and_increment()
        assert allowed is True
        assert "1/3" in msg

    def test_blocks_at_limit(self):
        rl = RateLimit("test_action", max_count=2, window_hours=1)
        rl.check_and_increment()
        rl.check_and_increment()
        allowed, msg = rl.check_and_increment()
        assert allowed is False
        assert "exceeded" in msg.lower()

    def test_window_reset(self):
        rl = RateLimit("test_action", max_count=1, window_hours=1)
        rl.check_and_increment()
        # Force window expiry
        rl.window_start = datetime.now(timezone.utc) - timedelta(hours=2)
        allowed, _ = rl.check_and_increment()
        assert allowed is True

    def test_reset_method(self):
        rl = RateLimit("test_action", max_count=1, window_hours=1)
        rl.check_and_increment()
        rl.reset()
        assert rl.current_count == 0


# ---------------------------------------------------------------------------
# ScopeRestriction
# ---------------------------------------------------------------------------

class TestScopeRestriction:
    def _make_adjustment(self, adj_type=AdjustmentType.PRIORITY_INCREASE, rule_id="R1"):
        return Adjustment(
            id="ADJ-001",
            rule_id=rule_id,
            type=adj_type,
            objective_id=None,
            description="test adjustment",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

    def test_allows_unrestricted(self):
        scope = ScopeRestriction(name="default", description="test")
        adj = self._make_adjustment()
        allowed, reason = scope.check_adjustment(adj)
        assert allowed is True

    def test_blocks_adjustment_type(self):
        scope = ScopeRestriction(
            name="limited",
            description="test",
            blocked_adjustment_types=["priority_increase"],
        )
        adj = self._make_adjustment(AdjustmentType.PRIORITY_INCREASE)
        allowed, reason = scope.check_adjustment(adj)
        assert allowed is False
        assert "blocked" in reason.lower()

    def test_blocks_rule(self):
        scope = ScopeRestriction(
            name="limited", description="test", blocked_rules=["R1"]
        )
        adj = self._make_adjustment(rule_id="R1")
        allowed, reason = scope.check_adjustment(adj)
        assert allowed is False

    def test_blocks_metric_type(self):
        scope = ScopeRestriction(
            name="limited", description="test", blocked_metric_types=["coverage"]
        )
        adj = self._make_adjustment()
        adj.parameters["objective_template"] = {"metric_type": "coverage"}
        allowed, _ = scope.check_adjustment(adj)
        assert allowed is False


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

class TestAuditLog:
    @pytest.fixture()
    def audit_log(self, tmp_path):
        return AuditLog(log_path=tmp_path / "audit.json")

    def test_log_event(self, audit_log):
        event = audit_log.log_event(
            AuditEventType.ADJUSTMENT_PROPOSED,
            "system",
            {"rule_id": "R1"},
        )
        assert event.id == "AUD-000001"

    def test_get_events(self, audit_log):
        audit_log.log_event(AuditEventType.ADJUSTMENT_PROPOSED, "system", {})
        audit_log.log_event(AuditEventType.OVERRIDE_APPLIED, "admin", {})
        events = audit_log.get_events()
        assert len(events) == 2

    def test_get_events_by_type(self, audit_log):
        audit_log.log_event(AuditEventType.ADJUSTMENT_PROPOSED, "system", {})
        audit_log.log_event(AuditEventType.OVERRIDE_APPLIED, "admin", {})
        events = audit_log.get_events(event_type=AuditEventType.OVERRIDE_APPLIED)
        assert len(events) == 1

    def test_get_events_for_adjustment(self, audit_log):
        audit_log.log_event(
            AuditEventType.ADJUSTMENT_PROPOSED, "system", {"adjustment_id": "ADJ-1"}
        )
        audit_log.log_event(
            AuditEventType.ADJUSTMENT_EXECUTED, "system", {"adjustment_id": "ADJ-1"}
        )
        events = audit_log.get_events_for_adjustment("ADJ-1")
        assert len(events) == 2

    def test_persistence(self, tmp_path):
        path = tmp_path / "audit.json"
        log1 = AuditLog(log_path=path)
        log1.log_event(AuditEventType.ADJUSTMENT_PROPOSED, "system", {})

        log2 = AuditLog(log_path=path)
        events = log2.get_events()
        assert len(events) == 1

    def test_truncation(self, tmp_path):
        log = AuditLog(log_path=tmp_path / "audit.json")
        # Log beyond the 10000 cap by setting events directly
        log._events = [{"dummy": i} for i in range(10001)]
        log._events = log._events[-10000:]
        assert len(log._events) == 10000


# ---------------------------------------------------------------------------
# SafetyGuard
# ---------------------------------------------------------------------------

class TestSafetyGuard:
    @pytest.fixture()
    def guard(self, tmp_path):
        audit_log = AuditLog(log_path=tmp_path / "audit.json")
        return SafetyGuard(audit_log=audit_log)

    def _make_adjustment(self, adj_type=AdjustmentType.PRIORITY_INCREASE, rule_id="R1"):
        return Adjustment(
            id="ADJ-001",
            rule_id=rule_id,
            type=adj_type,
            objective_id=None,
            description="test adjustment",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

    def test_pause_and_resume(self, guard):
        assert not guard.is_paused
        guard.pause_automation("admin", "maintenance")
        assert guard.is_paused
        guard.resume_automation("admin")
        assert not guard.is_paused

    def test_check_adjustment_when_paused(self, guard):
        guard.pause_automation("admin")
        adj = self._make_adjustment()
        allowed, reason = guard.check_adjustment(adj)
        assert allowed is False
        assert "paused" in reason.lower()

    def test_check_adjustment_allowed(self, guard):
        adj = self._make_adjustment()
        allowed, reason = guard.check_adjustment(adj)
        assert allowed is True

    def test_block_and_unblock_rule(self, guard):
        guard.block_rule("R1", "admin", "testing")
        adj = self._make_adjustment(rule_id="R1")
        allowed, _ = guard.check_adjustment(adj)
        assert allowed is False

        guard.unblock_rule("R1", "admin")
        allowed, _ = guard.check_adjustment(adj)
        assert allowed is True

    def test_block_rule_idempotent(self, guard):
        guard.block_rule("R1", "admin")
        guard.block_rule("R1", "admin")
        assert guard.scope.blocked_rules.count("R1") == 1

    def test_unblock_nonexistent_rule(self, guard):
        # Should not raise
        guard.unblock_rule("R_NONEXISTENT", "admin")
