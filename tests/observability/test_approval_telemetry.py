#!/usr/bin/env python3
"""
Integration Tests — Approval Telemetry Collector & SLA Monitoring
Phase 12 Wave 2 - D3.2 Deliverable

Tests the complete telemetry collection pipeline, SLA monitoring, and alert generation.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Add scripts/observability to path
sys.path.insert(0, str(Path(__file__).parent))

from approval_event_schema import (
    ApprovalEventValidator,
)
from approval_telemetry_collector import (
    ApprovalTelemetryCollector,
)
from sla_monitoring import (
    ApprovalServiceIntegration,
    ComplianceReporter,
    SLAMonitor,
)


class TestApprovalTelemetryCollector:
    """Test the approval telemetry collector."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = ApprovalTelemetryCollector(max_events=1000)
    
    def test_record_approval_request(self):
        """Test recording an approval request."""
        self.collector.record_approval_request(
            approval_id="apr-001",
            policy_id="D-001",
            policy_category="D",
            requester_id="agent-01",
            requester_role="release-operator",
            sla_seconds=14400,
        )
        
        assert len(self.collector.events) == 1
        event = self.collector.events[0]
        assert event["approval_id"] == "apr-001"
        assert event["policy_category"] == "D"
        assert event["event_type"] == "approval.request.submitted"
    
    def test_record_approval_decision_met_sla(self):
        """Test recording a decision that meets SLA."""
        sla_met, status = self.collector.record_approval_decision(
            approval_id="apr-001",
            policy_id="D-001",
            policy_category="D",
            approver_id="mgr-01",
            approver_role="release-manager",
            decision="approved",
            decision_time_seconds=3600,  # 1 hour (well within 4h SLA)
            stage=1,
            sla_seconds=14400,
        )
        
        assert sla_met is True
        assert status == "met"
    
    def test_record_approval_decision_breached_sla(self):
        """Test recording a decision that breaches SLA."""
        sla_met, status = self.collector.record_approval_decision(
            approval_id="apr-002",
            policy_id="D-001",
            policy_category="D",
            approver_id="mgr-01",
            approver_role="release-manager",
            decision="approved",
            decision_time_seconds=18000,  # 5 hours (exceeds 4h SLA)
            stage=1,
            sla_seconds=14400,
        )
        
        assert sla_met is False
        assert status == "breached"
    
    def test_escalation_tracking(self):
        """Test escalation event tracking."""
        self.collector.record_escalation(
            approval_id="apr-003",
            policy_id="D-001",
            policy_category="D",
            trigger_type="timeout",
            escalation_level="L1→L2",
            resolution_time_seconds=3600,
        )
        
        assert len(self.collector.events) == 1
        event = self.collector.events[0]
        assert event["event_type"] == "approval.escalated"
    
    def test_delegation_tracking(self):
        """Test delegation event tracking."""
        self.collector.record_delegation(
            source_role="release-manager",
            target_role="devops-lead",
            policy_category="D",
            delegation_id="del-001",
        )
        
        # Check counter was incremented
        assert "approval_delegation_count_total:release-manager:devops-lead:D" in self.collector.counters
    
    def test_cardinality_validation(self):
        """Test cardinality limit checking."""
        # Add metrics with various dimensions
        for i in range(10):
            for role in ["release-manager", "security-lead", "devops-lead"]:
                self.collector.record_approval_decision(
                    approval_id=f"apr-{i}",
                    policy_id="D-001",
                    policy_category="D",
                    approver_id=f"approver-{i}",
                    approver_role=role,
                    decision="approved",
                    decision_time_seconds=3600,
                    stage=1,
                    sla_seconds=14400,
                )
        
        cardinality = self.collector.validate_cardinality()
        assert cardinality["cardinality_safe"] is True
        assert cardinality["timeseries_count"] < 900
    
    def test_metrics_snapshot(self):
        """Test generating a metrics snapshot."""
        # Record multiple events
        self.collector.record_approval_request(
            approval_id="apr-001",
            policy_id="D-001",
            policy_category="D",
            requester_id="agent-01",
            requester_role="release-operator",
            sla_seconds=14400,
        )
        
        self.collector.record_approval_decision(
            approval_id="apr-001",
            policy_id="D-001",
            policy_category="D",
            approver_id="mgr-01",
            approver_role="release-manager",
            decision="approved",
            decision_time_seconds=3600,
            stage=1,
            sla_seconds=14400,
        )
        
        snapshot = self.collector.get_snapshot()
        assert snapshot.timestamp is not None
        assert snapshot.request_submitted > 0
        assert snapshot.sla_breached_count == 0


class TestApprovalEventValidator:
    """Test event schema validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ApprovalEventValidator(strict_mode=True)
    
    def test_valid_event(self):
        """Test validation of a valid event."""
        event = {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "approval.decision.made",
            "policy_id": "D-001",
            "policy_category": "D",
            "approval_id": "apr-001",
            "requester_id": "agent-01",
            "requester_role": "release-operator",
        }
        
        is_valid, errors = self.validator.validate_event(event)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_invalid_event_missing_required_field(self):
        """Test validation of event missing required field."""
        event = {
            "version": "1.0.0",
            # Missing timestamp
            "event_type": "approval.decision.made",
            "policy_id": "D-001",
            "policy_category": "D",
        }
        
        is_valid, errors = self.validator.validate_event(event)
        assert is_valid is False
        assert any("timestamp" in error.lower() for error in errors)
    
    def test_invalid_event_type(self):
        """Test validation of invalid event type."""
        event = {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "approval.invalid",  # Invalid
            "policy_id": "D-001",
            "policy_category": "D",
        }
        
        is_valid, errors = self.validator.validate_event(event)
        assert is_valid is False
        assert any("event_type" in error.lower() for error in errors)
    
    def test_invalid_policy_category(self):
        """Test validation of invalid policy category."""
        event = {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "approval.decision.made",
            "policy_id": "X-001",  # Invalid category
            "policy_category": "X",
        }
        
        is_valid, errors = self.validator.validate_event(event)
        assert is_valid is False
        assert any("policy_category" in error.lower() for error in errors)
    
    def test_sla_calculation_validation(self):
        """Test SLA calculation validation."""
        event = {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "approval.decision.made",
            "policy_id": "D-001",
            "policy_category": "D",
            "total_latency_seconds": 10000,
            "sla_seconds": 14400,
            "sla_met": False,  # Correct: 10000 < 14400 should be True
            "sla_status": "met",
        }
        
        is_valid, errors = self.validator.validate_event(event)
        assert is_valid is False
        assert any("sla" in error.lower() for error in errors)
    
    def test_batch_validation(self):
        """Test batch event validation."""
        events = [
            {
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "approval.request.submitted",
                "policy_id": "D-001",
                "policy_category": "D",
            }
            for _ in range(5)
        ]
        
        result = self.validator.validate_event_batch(events)
        assert result["total"] == 5
        assert result["valid"] == 5
        assert result["invalid"] == 0


class TestSLAMonitor:
    """Test SLA monitoring."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = ApprovalTelemetryCollector()
        self.escalation_calls = []
        
        def escalation_callback(approval_id, policy_cat, reason):
            self.escalation_calls.append({
                "approval_id": approval_id,
                "policy_category": policy_cat,
                "reason": reason,
            })
        
        self.sla_monitor = SLAMonitor(
            self.collector,
            escalation_callback=escalation_callback,
        )
    
    def test_track_approval_request(self):
        """Test tracking an approval request."""
        self.sla_monitor.track_approval_request(
            approval_id="apr-001",
            policy_category="D",
            policy_id="D-001",
            submitted_at=datetime.now(timezone.utc),
        )
        
        in_flight = self.sla_monitor.get_in_flight_approvals()
        assert len(in_flight) == 1
        assert in_flight[0]["policy_id"] == "D-001"
    
    def test_sla_met(self):
        """Test SLA met scenario."""
        self.sla_monitor.track_approval_request(
            approval_id="apr-001",
            policy_category="D",
            policy_id="D-001",
            submitted_at=datetime.now(timezone.utc),
        )
        
        result = self.sla_monitor.record_stage_decision(
            approval_id="apr-001",
            stage=1,
            decision_time_seconds=3600,  # 1 hour
            policy_category="D",
        )
        
        assert result["sla_status"] == "met"
        assert result["exceeded_by"] == 0
        assert result["escalation_triggered"] is False
        assert len(self.escalation_calls) == 0
    
    def test_sla_breached_triggers_escalation(self):
        """Test SLA breach triggers escalation."""
        self.sla_monitor.track_approval_request(
            approval_id="apr-002",
            policy_category="D",
            policy_id="D-001",
            submitted_at=datetime.now(timezone.utc),
        )
        
        result = self.sla_monitor.record_stage_decision(
            approval_id="apr-002",
            stage=1,
            decision_time_seconds=18000,  # 5 hours (exceeds 4h SLA)
            policy_category="D",
        )
        
        assert result["sla_status"] == "breached"
        assert result["exceeded_by"] > 0
        assert result["escalation_triggered"] is True
        assert len(self.escalation_calls) == 1
        assert self.escalation_calls[0]["approval_id"] == "apr-002"
    
    def test_sla_approaching(self):
        """Test SLA approaching threshold."""
        self.sla_monitor.track_approval_request(
            approval_id="apr-003",
            policy_category="D",
            policy_id="D-001",
            submitted_at=datetime.now(timezone.utc),
        )
        
        # 80% of 4h SLA
        result = self.sla_monitor.record_stage_decision(
            approval_id="apr-003",
            stage=1,
            decision_time_seconds=11520,  # 3.2 hours (80% of 4h)
            policy_category="D",
        )
        
        assert result["sla_status"] == "approaching"
        assert result["exceeded_by"] == 0
    
    def test_compliance_report(self):
        """Test generating compliance report."""
        # Create multiple requests with various outcomes
        for i in range(5):
            self.sla_monitor.track_approval_request(
                approval_id=f"apr-{i:03d}",
                policy_category="D",
                policy_id="D-001",
                submitted_at=datetime.now(timezone.utc),
            )
            
            decision_time = 3600 if i < 3 else 18000  # 3 met, 2 breached
            self.sla_monitor.record_stage_decision(
                approval_id=f"apr-{i:03d}",
                stage=1,
                decision_time_seconds=decision_time,
                policy_category="D",
            )
        
        report = self.sla_monitor.get_sla_compliance_report()
        
        assert report["total_requests"] == 5
        assert report["sla_met_count"] == 3
        assert report["sla_breached_count"] == 2
        assert report["sla_compliance_pct"] == 60.0


class TestApprovalServiceIntegration:
    """Test integration with approval service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = ApprovalTelemetryCollector()
        self.sla_monitor = SLAMonitor(self.collector)
        self.integration = ApprovalServiceIntegration(self.collector, self.sla_monitor)
    
    def test_workflow_integration(self):
        """Test complete approval workflow integration."""
        # 1. Submit request
        self.integration.on_request_submitted(
            approval_id="apr-001",
            policy_id="D-001",
            policy_category="D",
            requester_id="agent-orchestrator",
            requester_role="release-operator",
            sla_seconds=14400,
        )
        
        # 2. Make decision
        self.integration.on_decision_made(
            approval_id="apr-001",
            policy_id="D-001",
            policy_category="D",
            approver_id="mgr-01",
            approver_role="release-manager",
            decision="approved",
            decision_time_seconds=3600,
            stage=1,
            sla_seconds=14400,
        )
        
        # 3. Complete approval
        self.integration.on_approval_completed(approval_id="apr-001")
        
        # Verify tracking completed
        in_flight = self.sla_monitor.get_in_flight_approvals()
        assert len(in_flight) == 0  # Should be removed after completion
        
        # Verify events recorded
        assert len(self.collector.events) == 2  # Request + Decision


class TestComplianceReporter:
    """Test compliance reporting."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = ApprovalTelemetryCollector()
        self.sla_monitor = SLAMonitor(self.collector)
        self.reporter = ComplianceReporter(self.sla_monitor)
    
    def test_hourly_report_generation(self):
        """Test generating hourly compliance report."""
        report = self.reporter.generate_hourly_report()
        
        assert "period" in report
        assert report["period"] == "1h"
        assert "sla_compliance" in report
        assert "timestamp" in report
    
    def test_daily_report_aggregation(self):
        """Test generating daily report (aggregate of hourly)."""
        # Generate some hourly reports first
        for _ in range(24):
            self.reporter.generate_hourly_report()
        
        daily = self.reporter.generate_daily_report()
        
        assert "period" in daily
        assert daily["period"] == "24h"
        assert "aggregate_sla_compliance_pct" in daily


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    def test_complete_approval_workflow_with_monitoring(self):
        """Test complete workflow from request to completion."""
        # Initialize system
        collector = ApprovalTelemetryCollector()
        sla_monitor = SLAMonitor(collector)
        integration = ApprovalServiceIntegration(collector, sla_monitor)
        reporter = ComplianceReporter(sla_monitor)
        validator = ApprovalEventValidator()
        
        # Simulate multi-stage approval workflow
        approval_id = "apr-workflow-001"
        
        # Stage 1: Submit
        integration.on_request_submitted(
            approval_id=approval_id,
            policy_id="D-001",
            policy_category="D",
            requester_id="agent-01",
            requester_role="release-operator",
            sla_seconds=14400,
        )
        
        # Validate request event
        request_event = collector.events[0]
        is_valid, errors = validator.validate_event(request_event)
        assert is_valid is True
        
        # Stage 2: First decision (Release Manager)
        integration.on_decision_made(
            approval_id=approval_id,
            policy_id="D-001",
            policy_category="D",
            approver_id="mgr-01",
            approver_role="release-manager",
            decision="approved",
            decision_time_seconds=3600,
            stage=1,
            sla_seconds=14400,
        )
        
        # Stage 3: Second decision (Security Lead)
        integration.on_decision_made(
            approval_id=approval_id,
            policy_id="D-001",
            policy_category="D",
            approver_id="sec-01",
            approver_role="security-lead",
            decision="approved",
            decision_time_seconds=5400,  # 1.5 hours total
            stage=2,
            sla_seconds=14400,
        )
        
        # Complete workflow
        integration.on_approval_completed(approval_id=approval_id)
        
        # Generate reports
        snapshot = collector.get_snapshot()
        compliance = sla_monitor.get_sla_compliance_report()
        hourly = reporter.generate_hourly_report()
        
        # Assertions
        assert len(collector.events) == 3  # Request + 2 Decisions
        assert all(e["version"] == "1.0.0" for e in collector.events)
        assert snapshot.sla_breached_count == 0
        assert compliance["sla_compliance_pct"] > 0
        assert len(sla_monitor.get_in_flight_approvals()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
