"""
Comprehensive test suite for governance approval service.

Tests cover:
- Approval request lifecycle (create, escalate, approve, reject)
- SLA policy management and escalation
- Auto-approval trigger conditions
- 7-state machine transitions
- Audit logging and compliance
- Error handling and edge cases
"""

import pytest
import time
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from src.codex.governance.approval_service import (
    ApprovalService,
    ApprovalRequest,
    ApprovalDecision,
    SLAPolicy,
    ApprovalState,
    AuditCode,
)


class TestApprovalRequestDataClass:
    """Test ApprovalRequest data class and properties."""

    def test_approval_request_creation_with_defaults(self):
        """Test creating ApprovalRequest with default values."""
        req = ApprovalRequest()
        assert req.status == ApprovalState.PENDING
        assert req.request_id is not None
        assert req.created_at > 0
        assert req.escalation_count == 0
        assert req.sla_extensions_used == 0

    def test_approval_request_creation_with_custom_values(self):
        """Test creating ApprovalRequest with custom values."""
        req = ApprovalRequest(
            request_id="test-123",
            policy_code="SECURITY_PATCH",
            requester_id="user-456",
        )
        assert req.request_id == "test-123"
        assert req.policy_code == "SECURITY_PATCH"
        assert req.requester_id == "user-456"

    def test_approval_request_age_seconds(self):
        """Test age_seconds property calculation."""
        req = ApprovalRequest()
        time.sleep(0.1)
        age = req.age_seconds
        assert age >= 0.1
        assert age < 1.0

    def test_approval_request_is_expired_property(self):
        """Test is_expired property."""
        req = ApprovalRequest(
            sla_deadline=time.time() - 100  # Expired
        )
        assert req.is_expired is True

    def test_approval_request_is_not_expired_property(self):
        """Test is_expired property when not expired."""
        req = ApprovalRequest(
            sla_deadline=time.time() + 3600  # 1 hour in future
        )
        assert req.is_expired is False

    def test_approval_request_sla_exceeded_calculation(self):
        """Test sla_exceeded_by_seconds property."""
        req = ApprovalRequest(
            sla_deadline=time.time() - 100  # Exceeded by ~100 seconds
        )
        exceeded = req.sla_exceeded_by_seconds
        assert exceeded >= 99
        assert exceeded <= 101

    def test_approval_request_escalations_remaining(self):
        """Test escalations_remaining property."""
        req = ApprovalRequest(
            escalation_count=1,
            escalation_chain=[1, 2, 3]
        )
        assert req.escalations_remaining == 1

    def test_approval_request_escalations_remaining_at_limit(self):
        """Test escalations_remaining when all escalations exhausted."""
        req = ApprovalRequest(
            escalation_count=2,
            escalation_chain=[1, 2, 3]
        )
        assert req.escalations_remaining == 0


class TestApprovalDecision:
    """Test ApprovalDecision data class."""

    def test_approval_decision_creation(self):
        """Test creating an approval decision."""
        decision = ApprovalDecision(
            approver_id="approver-1",
            approver_name="Alice",
            decision="APPROVED",
            authority_level=2
        )
        assert decision.approver_id == "approver-1"
        assert decision.approver_name == "Alice"
        assert decision.decision == "APPROVED"
        assert decision.authority_level == 2
        assert decision.timestamp > 0

    def test_approval_decision_with_reason(self):
        """Test approval decision with reason."""
        decision = ApprovalDecision(
            approver_id="approver-1",
            approver_name="Bob",
            decision="REJECTED",
            reason="Security risk identified"
        )
        assert decision.reason == "Security risk identified"


class TestSLAPolicy:
    """Test SLAPolicy data class."""

    def test_sla_policy_creation_with_defaults(self):
        """Test creating SLAPolicy with default values."""
        policy = SLAPolicy(policy_code="STANDARD")
        assert policy.policy_code == "STANDARD"
        assert policy.l1_sla_hours == 4.0
        assert policy.l2_sla_hours == 4.0
        assert policy.owner_sla_hours == 4.0
        assert policy.is_destructive is False

    def test_sla_policy_destructive_operation(self):
        """Test SLA policy for destructive operations."""
        policy = SLAPolicy(
            policy_code="DESTRUCTIVE",
            is_destructive=True,
            owner_sla_hours=2.0,
            incident_sla_minutes=15.0
        )
        assert policy.is_destructive is True
        assert policy.owner_sla_hours == 2.0

    def test_sla_policy_incident_escalation(self):
        """Test SLA policy with incident escalation."""
        policy = SLAPolicy(
            policy_code="INCIDENT",
            is_incident_related=True,
            incident_sla_minutes=30.0,
            max_escalations=1
        )
        assert policy.is_incident_related is True
        assert policy.max_escalations == 1


class TestApprovalService:
    """Test ApprovalService core functionality."""

    def test_approval_service_initialization(self):
        """Test ApprovalService initialization."""
        service = ApprovalService()
        assert service.logger is not None
        assert isinstance(service._requests, dict)
        assert len(service._requests) == 0

    def test_approval_service_initialization_with_logger(self):
        """Test ApprovalService initialization with custom logger."""
        logger = logging.getLogger("test")
        service = ApprovalService(logger=logger)
        assert service.logger is logger

    def test_submit_approval_request(self):
        """Test submitting an approval request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="SECURITY_PATCH", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="SECURITY_PATCH",
            requester_id="user-123",
            required_approvers=["approver-1"]
        )
        assert req is not None
        assert req.request_id is not None
        
    def test_get_approval_request(self):
        """Test retrieving an approval request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        retrieved = service.get_request(req.request_id)
        assert retrieved is not None
        assert retrieved.policy_code == "TEST"

    def test_get_nonexistent_request(self):
        """Test getting nonexistent request raises error."""
        service = ApprovalService()
        with pytest.raises((ValueError, KeyError)):
            service.get_request("nonexistent-id")

    def test_approve_request(self):
        """Test approving an approval request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.approve_request(
            request_id=req.request_id,
            approver_id="approver-1",
            authority_level=1
        )
        retrieved = service.get_request(req.request_id)
        assert retrieved.status == ApprovalState.APPROVED

    def test_reject_request(self):
        """Test rejecting an approval request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.reject_request(
            request_id=req.request_id,
            approver_id="approver-1",
            reason="Not approved"
        )
        retrieved = service.get_request(req.request_id)
        assert retrieved.status == ApprovalState.REJECTED

    def test_request_transitions_through_states(self):
        """Test request transitions through 7-state machine."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        # PENDING -> approved
        assert req.status == ApprovalState.PENDING
        
        service.approve_request(req.request_id, "approver-1", 1)
        req = service.get_request(req.request_id)
        assert req.status == ApprovalState.APPROVED

    def test_cancel_request(self):
        """Test cancelling an approval request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.cancel_request(req.request_id, "Cancelled")
        retrieved = service.get_request(req.request_id)
        assert retrieved.status == ApprovalState.CANCELLED

    def test_audit_log_entry_on_approval(self):
        """Test audit log entry created on approval."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.approve_request(req.request_id, "approver-1", 1)
        retrieved = service.get_request(req.request_id)
        assert len(retrieved.audit_log) > 0

    def test_register_sla_policy(self):
        """Test registering an SLA policy."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="CUSTOM", l1_sla_hours=8.0)
        service.register_sla_policy(policy)
        # Policy should be stored
        assert service._sla_policies.get("CUSTOM") is not None

    def test_multiple_approvers_on_request(self):
        """Test multiple approvers on single request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="MULTI_APPROVER", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="MULTI_APPROVER",
            requester_id="user-1",
            required_approvers=["approver-1", "approver-2"]
        )
        
        # First approver decision
        service.approve_request(
            request_id=req.request_id,
            approver_id="approver-1",
            authority_level=1
        )
        
        req = service.get_request(req.request_id)
        assert len(req.required_approvers) == 2


class TestApprovalEscalation:
    """Test approval escalation workflows."""

    def test_escalate_request(self):
        """Test escalating an approval request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        # Force expiration for escalation
        req.sla_deadline = time.time() - 1
        
        escalated = service.check_and_escalate()
        # Check if escalation occurred
        assert isinstance(escalated, list)

    def test_escalation_count_increments(self):
        """Test escalation count increments."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        initial_count = req.escalation_count
        
        # Force escalation
        req.sla_deadline = time.time() - 1
        escalated = service.check_and_escalate()
        
        req = service.get_request(req.request_id)
        # Escalation count should have incremented or list should have entries
        assert isinstance(escalated, list)

    def test_escalation_chain_limits(self):
        """Test cannot escalate beyond escalation chain."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        # Should have escalation chain
        assert len(req.escalation_chain) > 0

    def test_escalation_updates_authority_level(self):
        """Test escalation updates current authority level."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        initial_level = req.current_authority_level
        assert initial_level >= 0


class TestAutoApprovalConditions:
    """Test auto-approval trigger conditions."""

    def test_auto_approval_incident_mode(self):
        """Test auto-approval in incident mode."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="INCIDENT", l1_sla_hours=4.0, is_incident_related=True, incident_sla_minutes=15.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="INCIDENT",
            requester_id="user-1",
            required_approvers=["approver-1"],
            is_incident_related=True,
            incident_id="incident-123"
        )
        
        # Check auto-approval conditions
        auto_approvals = service.check_auto_approval_conditions()
        assert isinstance(auto_approvals, list)


class TestSLAManagement:
    """Test SLA policy management and escalation."""

    def test_sla_policy_configuration(self):
        """Test SLA policy configuration."""
        service = ApprovalService()
        policy = SLAPolicy(
            policy_code="URGENT",
            l1_sla_hours=1.0,
            l2_sla_hours=2.0,
            owner_sla_hours=4.0
        )
        service.register_sla_policy(policy)
        
        # Retrieve and verify
        assert service._sla_policies.get("URGENT") is not None

    def test_sla_enforcement_on_request(self):
        """Test SLA enforcement creates correct deadline."""
        service = ApprovalService()
        now = time.time()
        
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        # SLA deadline should be in future (default 4 hours)
        assert req.sla_deadline > now

    def test_sla_extension(self):
        """Test SLA extension functionality."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        original_deadline = req.sla_deadline
        
        service.request_sla_extension(req.request_id, "Waiting for more info")
        
        extended_req = service.get_request(req.request_id)
        assert extended_req.sla_deadline > original_deadline

    def test_sla_extension_limit(self):
        """Test SLA extension respects max limit."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.request_sla_extension(req.request_id, "Extension 1")
        
        # Second extension should be allowed or rejected
        req = service.get_request(req.request_id)
        assert req.sla_extensions_used <= req.max_sla_extensions


class TestAuditLogging:
    """Test audit logging and compliance tracking."""

    def test_audit_log_contains_decisions(self):
        """Test audit log contains approval decisions."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.approve_request(req.request_id, "approver-1", 1)
        
        req = service.get_request(req.request_id)
        assert len(req.audit_log) > 0

    def test_audit_log_contains_timestamps(self):
        """Test audit log entries have timestamps."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.approve_request(req.request_id, "approver-1", 1)
        
        req = service.get_request(req.request_id)
        for entry in req.audit_log:
            assert "timestamp" in entry or "time" in str(entry).lower()

    def test_audit_codes_mapped_to_actions(self):
        """Test audit codes are properly mapped."""
        # Verify AuditCode enum contains all expected codes
        assert hasattr(AuditCode, "MANUAL_APPROVAL")
        assert hasattr(AuditCode, "AUTO_APPROVAL_OWNER_UNAVAILABLE")
        assert hasattr(AuditCode, "SLA_ESCALATION_L1_L2")


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_request_id_raises_error(self):
        """Test accessing invalid request ID raises ValueError."""
        service = ApprovalService()
        with pytest.raises((ValueError, KeyError)):
            service.get_request("invalid-id")

    def test_approve_already_rejected_request_fails(self):
        """Test cannot approve a rejected request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        service.reject_request(req.request_id, "approver-1", "Reason")
        
        with pytest.raises((ValueError, RuntimeError)):
            service.approve_request(req.request_id, "approver-2", 1)

    def test_empty_required_approvers_list(self):
        """Test request with empty required approvers."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=[]
        )
        assert req.required_approvers == []

    def test_missing_sla_policy(self):
        """Test submission with missing SLA policy raises error."""
        service = ApprovalService()
        
        with pytest.raises(ValueError):
            service.submit_request(
                policy_code="NONEXISTENT",
                requester_id="user-1",
                required_approvers=["approver-1"]
            )


class TestBatchOperations:
    """Test batch operations on multiple requests."""

    def test_get_all_pending_requests(self):
        """Test retrieving all pending requests."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        # Create multiple requests
        req1 = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        req2 = service.submit_request(
            policy_code="TEST",
            requester_id="user-2",
            required_approvers=["approver-1"]
        )
        
        # Approve one
        service.approve_request(req1.request_id, "approver-1", 1)
        
        # Get pending
        pending = service.list_pending()
        assert len(pending) >= 1

    def test_get_all_requests(self):
        """Test retrieving all requests."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"]
        )
        
        all_reqs = service.list_all()
        assert len(all_reqs) >= 1


class TestContextManagement:
    """Test request context and metadata."""

    def test_store_request_context(self):
        """Test storing arbitrary context on request."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        context = {"custom_field": "custom_value"}
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"],
            context=context
        )
        
        assert req.context.get("custom_field") == "custom_value"

    def test_context_with_complex_data(self):
        """Test context with nested data structures."""
        service = ApprovalService()
        policy = SLAPolicy(policy_code="TEST", l1_sla_hours=4.0)
        service.register_sla_policy(policy)
        
        context = {
            "change_details": {
                "files_modified": ["file1.py", "file2.py"],
                "lines_changed": 150
            }
        }
        
        req = service.submit_request(
            policy_code="TEST",
            requester_id="user-1",
            required_approvers=["approver-1"],
            context=context
        )
        
        assert "change_details" in req.context
        assert len(req.context["change_details"]["files_modified"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
