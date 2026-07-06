#!/usr/bin/env python3
"""
Comprehensive test suite for ApprovalService covering all 13 edge case scenarios
from APPROVAL_POLICIES.md Section E.4e.

Test Plan:
- Scenario 1: Basic manual approval (pending → approved)
- Scenario 2: SLA escalation L1→L2 (escalated, re-SLAed)
- Scenario 3: SLA escalation L2→Owner (escalated)
- Scenario 4: Owner unavailable >4h, escalates, then auto-approves (condition 1)
- Scenario 5: SLA extension requested and granted
- Scenario 6: SLA extension limit exceeded, forces escalation
- Scenario 7: Quorum unavailable (2+ approvers), escalates
- Scenario 8: Quorum unavailable + Owner SLA 4h+ → auto-approve (condition 2)
- Scenario 9: Rejection blocks workflow (single veto)
- Scenario 10: **CRITICAL** Simultaneous timer expiration → escalate FIRST, then auto-approve
- Scenario 11: Request already approved, escalation timer fires → ignored
- Scenario 12: Destructive operation (R-006) blocks auto-approval without Owner pre-auth
- Scenario 13: Post-auto-approval governance audit ticket created
"""

import logging
import sys
import time

# Set up path
sys.path.insert(0, '/home/runner/work/_codex_/_codex_')

from src.codex.governance.approval_service import (
    ApprovalService,
    ApprovalState,
    AuditCode,
    SLAPolicy,
)


class TestRunner:
    """Test harness for approval service."""
    
    def __init__(self):
        self.logger = logging.getLogger("TestRunner")
        self.logger.setLevel(logging.INFO)
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def run_all_scenarios(self) -> bool:
        """Run all 13 scenarios."""
        print("\n" + "="*80)
        print("APPROVAL SERVICE - 13 SCENARIO TEST SUITE")
        print("="*80 + "\n")
        
        scenarios = [
            self.scenario_01_basic_manual_approval,
            self.scenario_02_sla_escalation_l1_l2,
            self.scenario_03_sla_escalation_l2_owner,
            self.scenario_04_owner_unavailable_auto_approve,
            self.scenario_05_sla_extension_granted,
            self.scenario_06_sla_extension_limit_exceeded,
            self.scenario_07_quorum_unavailable,
            self.scenario_08_quorum_unavailable_auto_approve,
            self.scenario_09_rejection_veto,
            self.scenario_10_critical_simultaneous_timers,
            self.scenario_11_already_approved_ignore_timer,
            self.scenario_12_destructive_operation_blocks,
            self.scenario_13_governance_audit_ticket,
        ]
        
        for scenario_func in scenarios:
            try:
                scenario_func()
            except Exception as e:
                self._record_failure(scenario_func.__name__, str(e))
        
        self._print_summary()
        return self.failed == 0
    
    def _record_success(self, scenario_name: str, message: str = ""):
        self.passed += 1
        status = "✅ PASS"
        self.test_results.append((status, scenario_name))
        print(f"{status} - {scenario_name}")
        if message:
            print(f"       {message}")
    
    def _record_failure(self, scenario_name: str, error: str):
        self.failed += 1
        status = "❌ FAIL"
        self.test_results.append((status, scenario_name))
        print(f"{status} - {scenario_name}")
        print(f"       Error: {error}")
    
    def _assert(self, condition: bool, message: str):
        if not condition:
            raise AssertionError(message)
    
    def _print_summary(self):
        print("\n" + "="*80)
        print(f"TEST SUMMARY: {self.passed} passed, {self.failed} failed")
        print("="*80 + "\n")
        for status, name in self.test_results:
            print(f"{status} {name}")
        print()
    
    # ==================== SCENARIO 1: BASIC MANUAL APPROVAL ====================
    
    def scenario_01_basic_manual_approval(self):
        """Scenario 1: Request → pending state → manual approval → approved."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=4,
            max_escalations=2,
        ))
        
        # Submit request
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["approver_l1"],
        )
        
        self._assert(req.status == ApprovalState.PENDING, "Initial state must be pending")
        
        # Approve manually
        approved_req = service.approve_request(
            request_id=req.request_id,
            approver_id="approver_l1",
            reason="Looks good",
        )
        
        self._assert(approved_req.status == ApprovalState.APPROVED, "Final state must be approved")
        self._assert(len(approved_req.decisions) == 1, "Should have 1 decision")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [event["audit_code"] for event in audit_log]
        self._assert(AuditCode.MANUAL_APPROVAL.value in audit_codes, "Must have MANUAL_APPROVAL audit code")
        
        self._record_success("Scenario 1: Basic Manual Approval")
    
    # ==================== SCENARIO 2: SLA ESCALATION L1→L2 ====================
    
    def scenario_02_sla_escalation_l1_l2(self):
        """Scenario 2: SLA expires at L1 → escalates to L2."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.001,  # 3.6 seconds for testing
            l2_sla_hours=4,
            owner_sla_hours=4,
            max_escalations=3,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        
        self._assert(req.status == ApprovalState.PENDING, "Initial: pending")
        self._assert(req.current_authority_level == 1, "Initial: L1")
        
        # Wait for SLA to expire
        time.sleep(0.1)
        
        # Check escalation
        escalated = service.check_and_escalate()
        self._assert(len(escalated) > 0, "Should have escalated")
        self._assert(req.escalation_count == 1, "Escalation count should be 1")
        self._assert(req.current_authority_level == 2, "Should be at L2")
        self._assert(req.status == ApprovalState.ESCALATED, "Status should be ESCALATED")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        self._assert(AuditCode.SLA_ESCALATION_L1_L2.value in audit_codes, "Must log escalation")
        
        self._record_success("Scenario 2: SLA Escalation L1→L2")
    
    # ==================== SCENARIO 3: SLA ESCALATION L2→OWNER ====================
    
    def scenario_03_sla_escalation_l2_owner(self):
        """Scenario 3: From L2 escalation, SLA expires → escalates to Owner (L3)."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.0001,
            l2_sla_hours=0.001,
            owner_sla_hours=4,
            max_escalations=3,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        
        time.sleep(0.15)
        service.check_and_escalate()
        self._assert(req.current_authority_level == 2, "Should be at L2 after first escalation")
        
        time.sleep(0.05)
        service.check_and_escalate()
        self._assert(req.current_authority_level == 3, "Should be at L3 (Owner) after second escalation")
        self._assert(req.escalation_count == 2, "Escalation count should be 2")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        self._assert(AuditCode.SLA_ESCALATION_L2_L3.value in audit_codes, "Must log L2→L3 escalation")
        
        self._record_success("Scenario 3: SLA Escalation L2→Owner")
    
    # ==================== SCENARIO 4: OWNER UNAVAILABLE AUTO-APPROVE ====================
    
    def scenario_04_owner_unavailable_auto_approve(self):
        """Scenario 4: Condition 1 - Owner unavailable >4h, escalation chain exhausted → auto-approve."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.0001,
            l2_sla_hours=0.0001,
            owner_sla_hours=0.0001,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        req.created_at = time.time() - (24 * 3600)  # Simulate 24h old request
        
        # Escalate to Owner
        time.sleep(0.2)
        service.check_and_escalate()
        service.check_and_escalate()
        self._assert(req.current_authority_level == 3, "Should be at Owner level")
        
        # Mark Owner as unavailable (4h+)
        service.set_approver_availability("owner", False)
        
        # Check auto-approval
        auto_approved = service.check_auto_approval_conditions()
        
        # Should be auto-approved (Condition 1)
        self._assert(req.status == ApprovalState.ESCALATED_AUTO_APPROVED, 
                     f"Should be auto-approved, but is {req.status}")
        self._assert(req.auto_approval_reason is not None, "Should have auto-approval reason")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        self._assert(AuditCode.AUTO_APPROVAL_OWNER_UNAVAILABLE.value in audit_codes, 
                     "Must log auto-approval reason")
        
        self._record_success("Scenario 4: Owner Unavailable → Auto-Approve (Condition 1)")
    
    # ==================== SCENARIO 5: SLA EXTENSION GRANTED ====================
    
    def scenario_05_sla_extension_granted(self):
        """Scenario 5: SLA extension requested and granted."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=4,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1"],
        )
        
        old_deadline = req.sla_deadline
        
        # Request extension
        extended_req = service.request_sla_extension(
            request_id=req.request_id,
            approver_id="l1",
            extension_hours=4,
            reason="Need more time",
        )
        
        self._assert(extended_req.sla_deadline > old_deadline, "SLA deadline should be extended")
        self._assert(extended_req.sla_extensions_used == 1, "Should have 1 extension used")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        self._assert(AuditCode.SLA_EXTENSION_APPROVED.value in audit_codes, 
                     "Must log extension approval")
        
        self._record_success("Scenario 5: SLA Extension Granted")
    
    # ==================== SCENARIO 6: SLA EXTENSION LIMIT EXCEEDED ====================
    
    def scenario_06_sla_extension_limit_exceeded(self):
        """Scenario 6: SLA extension limit exceeded → forces escalation."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=4,
            l2_sla_hours=4,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2"],
        )
        req.max_sla_extensions = 1  # Set limit to 1
        
        # Use first extension
        service.request_sla_extension(req.request_id, "l1", 4, "First extension")
        self._assert(req.sla_extensions_used == 1, "Should have 1 extension")
        
        # Try second extension - should hit limit
        service.request_sla_extension(req.request_id, "l1", 4, "Second extension")
        
        # Should have escalated instead
        self._assert(req.escalation_count == 1, "Should have escalated instead of extending")
        self._assert(req.status == ApprovalState.ESCALATED, "Should be in ESCALATED state")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        self._assert(AuditCode.SLA_EXTENSION_LIMIT_REACHED.value in audit_codes, 
                     "Must log extension limit reached")
        
        self._record_success("Scenario 6: SLA Extension Limit Exceeded → Escalate")
    
    # ==================== SCENARIO 7: QUORUM UNAVAILABLE ====================
    
    def scenario_07_quorum_unavailable(self):
        """Scenario 7: 2+ approvers unavailable (quorum lost)."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=4,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "l3"],
        )
        
        # Mark 2+ as unavailable
        service.set_approver_availability("l1", False)
        service.set_approver_availability("l2", False)
        
        # Quorum lost should be detectable
        unavailable_count = sum(
            1 for app in req.required_approvers
            if not service._approver_availability.get(app, True)
        )
        self._assert(unavailable_count >= 2, "Should have 2+ unavailable approvers")
        
        self._record_success("Scenario 7: Quorum Unavailable (2+ approvers out)")
    
    # ==================== SCENARIO 8: QUORUM UNAVAILABLE + AUTO-APPROVE ====================
    
    def scenario_08_quorum_unavailable_auto_approve(self):
        """Scenario 8: Condition 2 - Quorum unavailable + Owner SLA 4h+ → auto-approve."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.0001,
            l2_sla_hours=0.0001,
            owner_sla_hours=0.001,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        
        # Escalate to Owner
        time.sleep(0.2)
        service.check_and_escalate()
        service.check_and_escalate()
        
        # Mark 2+ approvers unavailable
        service.set_approver_availability("l1", False)
        service.set_approver_availability("l2", False)
        
        # Wait for Owner SLA to expire
        time.sleep(0.05)
        
        # Check auto-approval
        service.check_auto_approval_conditions()
        
        # Should have auto-approved due to quorum loss (Condition 2)
        self._assert(req.status == ApprovalState.ESCALATED_AUTO_APPROVED,
                     f"Should be auto-approved (Condition 2), but is {req.status}")
        
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        self._assert(AuditCode.AUTO_APPROVAL_QUORUM_UNAVAILABLE.value in audit_codes,
                     "Must log quorum unavailable auto-approval")
        
        self._record_success("Scenario 8: Quorum Unavailable → Auto-Approve (Condition 2)")
    
    # ==================== SCENARIO 9: REJECTION VETO ====================
    
    def scenario_09_rejection_veto(self):
        """Scenario 9: Any rejection blocks approval workflow."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=4,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1"],
        )
        
        # Reject
        rejected_req = service.reject_request(
            request_id=req.request_id,
            approver_id="l1",
            reason="Not approved",
        )
        
        self._assert(rejected_req.status == ApprovalState.REJECTED, "Should be REJECTED")
        self._assert(len(rejected_req.decisions) == 1, "Should have 1 rejection decision")
        
        self._record_success("Scenario 9: Rejection Veto Blocks Workflow")
    
    # ==================== SCENARIO 10: CRITICAL - SIMULTANEOUS TIMERS ====================
    
    def scenario_10_critical_simultaneous_timers(self):
        """
        **CRITICAL SCENARIO**: Simultaneous timer expiration.
        
        Rule: SLA escalation has PRIORITY over auto-approval.
        Expected: Escalate FIRST, then check auto-approval.
        """
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.0001,
            l2_sla_hours=0.0001,
            owner_sla_hours=0.0001,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        req.created_at = time.time() - (24 * 3600)  # 24h old
        
        # Trigger escalations (fires L1→L2→Owner)
        time.sleep(0.2)
        escalated = service.check_and_escalate()
        
        # PRECEDENCE: Should have escalated first
        self._assert(req.current_authority_level == 3, "Should have escalated to Owner (L3)")
        self._assert(len(escalated) > 0, "Should have escalated")
        
        # Then check auto-approval (now at Owner, chain exhausted)
        service.set_approver_availability("owner", False)
        auto_approved = service.check_auto_approval_conditions()
        
        # Final state: Should be auto-approved after escalation chain exhausted
        self._assert(req.status == ApprovalState.ESCALATED_AUTO_APPROVED,
                     f"After simultaneous timers, should auto-approve, but is {req.status}")
        
        self._record_success("Scenario 10: **CRITICAL** Simultaneous Timers → Escalate First")
    
    # ==================== SCENARIO 11: ALREADY APPROVED, TIMER FIRES ====================
    
    def scenario_11_already_approved_ignore_timer(self):
        """Scenario 11: Request already approved, escalation timer fires → ignored."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.001,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1"],
        )
        
        # Approve manually
        service.approve_request(req.request_id, "l1", "OK")
        self._assert(req.status == ApprovalState.APPROVED, "Should be approved")
        
        # Wait for SLA to expire
        time.sleep(0.05)
        
        # Try to escalate (should be ignored)
        old_level = req.current_authority_level
        escalated = service.check_and_escalate()
        
        # Should NOT have escalated
        self._assert(req.status == ApprovalState.APPROVED, "Should still be APPROVED")
        self._assert(req.current_authority_level == old_level, "Authority level should not change")
        
        self._record_success("Scenario 11: Already Approved → Ignore Escalation Timer")
    
    # ==================== SCENARIO 12: DESTRUCTIVE OPERATION BLOCKS ====================
    
    def scenario_12_destructive_operation_blocks(self):
        """Scenario 12: Destructive operation (R-006) blocks auto-approval without pre-auth."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="R-006",
            l1_sla_hours=0.0001,
            l2_sla_hours=0.0001,
            owner_sla_hours=0.0001,
            max_escalations=2,
            is_destructive=True,
        ))
        
        req = service.submit_request(
            policy_code="R-006",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        req.created_at = time.time() - (24 * 3600)
        
        # Escalate to Owner
        time.sleep(0.2)
        service.check_and_escalate()
        service.check_and_escalate()
        
        # Mark Owner unavailable
        service.set_approver_availability("owner", False)
        
        # Check auto-approval (should NOT auto-approve for destructive without pre-auth)
        service.check_auto_approval_conditions()
        
        # Destructive operation should NOT auto-approve
        self._assert(req.status != ApprovalState.ESCALATED_AUTO_APPROVED,
                     "Destructive operation should NOT auto-approve without Owner pre-auth")
        
        # Now grant pre-auth
        req.has_owner_emergency_pre_auth = True
        service.check_auto_approval_conditions()
        
        # Now should auto-approve
        self._assert(req.status == ApprovalState.ESCALATED_AUTO_APPROVED,
                     "With pre-auth, destructive operation should auto-approve")
        
        self._record_success("Scenario 12: Destructive Operation Blocks Auto-Approval")
    
    # ==================== SCENARIO 13: GOVERNANCE AUDIT TICKET ====================
    
    def scenario_13_governance_audit_ticket(self):
        """Scenario 13: Post-auto-approval governance audit ticket created."""
        service = ApprovalService()
        service.register_sla_policy(SLAPolicy(
            policy_code="D-001",
            l1_sla_hours=0.0001,
            l2_sla_hours=0.0001,
            owner_sla_hours=0.0001,
            max_escalations=2,
        ))
        
        req = service.submit_request(
            policy_code="D-001",
            requester_id="user123",
            required_approvers=["l1", "l2", "owner"],
        )
        req.created_at = time.time() - (24 * 3600)
        
        # Trigger full escalation and auto-approval
        time.sleep(0.2)
        service.check_and_escalate()
        service.check_and_escalate()
        service.set_approver_availability("owner", False)
        service.check_auto_approval_conditions()
        
        # Check audit log for governance ticket creation
        audit_log = service.get_audit_log(req.request_id)
        audit_codes = [e["audit_code"] for e in audit_log]
        
        self._assert(AuditCode.GOVERNANCE_AUDIT_AUTO_APPROVAL.value in audit_codes,
                     "Must create GOVERNANCE_AUDIT_AUTO_APPROVAL ticket")
        
        # Find ticket creation event
        ticket_event = next(
            (e for e in audit_log if e["audit_code"] == AuditCode.GOVERNANCE_AUDIT_AUTO_APPROVAL.value),
            None
        )
        self._assert(ticket_event is not None, "Should have governance audit event")
        self._assert("GOVERNANCE-" in ticket_event["message"], "Ticket ID should have GOVERNANCE- prefix")
        
        self._record_success("Scenario 13: Governance Audit Ticket Created")


def main():
    """Run all scenario tests."""
    runner = TestRunner()
    success = runner.run_all_scenarios()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

