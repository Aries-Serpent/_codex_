"""Approval Router Module — Route T2/T3 decisions to @mbaetiong.

This module:
- Routes T2/T3 decisions to owner for approval
- Generates proposal packets
- Tracks approval time and decisions
- Enforces SLAs (T2: <24h, T3: <7d)
- Escalates on timeout
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from orchestration.healing.action_executor import ExecutionPlan
from orchestration.healing.strategy_generator import RepairStrategy

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """Status of approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SLA_EXCEEDED = "sla_exceeded"
    ESCALATED = "escalated"


@dataclass
class ApprovalRequest:
    """Approval request for T2/T3 action."""

    request_id: str
    strategy_id: str
    incident_id: str
    tier: str  # T2 or T3
    description: str
    risk_assessment: Dict[str, Any]
    evidence: List[str]
    actions_summary: List[str]
    created_at: str
    sla_expires_at: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: str = "@mbaetiong"
    approval_notes: Optional[str] = None
    approved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "strategy_id": self.strategy_id,
            "incident_id": self.incident_id,
            "tier": self.tier,
            "description": self.description,
            "risk_assessment": self.risk_assessment,
            "evidence": self.evidence,
            "actions_summary": self.actions_summary,
            "created_at": self.created_at,
            "sla_expires_at": self.sla_expires_at,
            "status": self.status.value,
            "approver": self.approver,
            "approval_notes": self.approval_notes,
            "approved_at": self.approved_at,
        }


@dataclass
class ApprovalDecision:
    """Decision on approval request."""

    request_id: str
    approved: bool
    timestamp: str
    approver: str = "@mbaetiong"
    notes: Optional[str] = None
    escalation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "approved": self.approved,
            "timestamp": self.timestamp,
            "approver": self.approver,
            "notes": self.notes,
            "escalation_reason": self.escalation_reason,
        }


class ApprovalRouter:
    """Routes approval decisions to @mbaetiong."""

    # In-memory storage (would be persistent in production)
    _pending_requests: Dict[str, ApprovalRequest] = {}
    _approval_history: List[ApprovalDecision] = []

    @classmethod
    def route_approval_request(
        cls, strategy: RepairStrategy, plan: ExecutionPlan
    ) -> ApprovalRequest:
        """Route strategy to approval.

        Args:
            strategy: RepairStrategy to approve
            plan: ExecutionPlan with tier

        Returns:
            ApprovalRequest routed to owner
        """
        import uuid

        request_id = f"appr_{strategy.incident_id}_{uuid.uuid4().hex[:6]}"
        now = datetime.now(timezone.utc)

        # Calculate SLA based on tier
        if plan.tier == "T2":
            sla_hours = 24
        elif plan.tier == "T3":
            sla_hours = 7 * 24  # 7 days
        else:
            sla_hours = 24

        sla_expires = now + timedelta(hours=sla_hours)

        # Build evidence from incident
        evidence = [h.description for h in strategy.actions]

        # Summarize actions
        actions_summary = [
            f"{a.action_type.value}: {a.description}" for a in strategy.actions
        ]

        # Build risk assessment
        risk_assessment = {
            "success_probability": strategy.success_probability,
            "risk_score": strategy.risk_score,
            "estimated_mttr_sec": strategy.estimated_mttr_sec,
            "tier": plan.tier,
            "requires_approval": strategy.requires_approval,
        }

        # Create request
        request = ApprovalRequest(
            request_id=request_id,
            strategy_id=strategy.strategy_id,
            incident_id=strategy.incident_id,
            tier=plan.tier,
            description=strategy.description,
            risk_assessment=risk_assessment,
            evidence=evidence,
            actions_summary=actions_summary,
            created_at=now.isoformat(),
            sla_expires_at=sla_expires.isoformat(),
            status=ApprovalStatus.PENDING,
            approver="@mbaetiong",
        )

        # Store request
        cls._pending_requests[request_id] = request

        logger.info(
            f"Routed approval request {request_id} for strategy {strategy.strategy_id} "
            f"to @mbaetiong (tier: {plan.tier}, SLA: {sla_hours}h)"
        )

        return request

    @classmethod
    def record_approval_decision(
        cls,
        request_id: str,
        approved: bool,
        approver: str = "@mbaetiong",
        notes: Optional[str] = None,
    ) -> ApprovalDecision:
        """Record approval decision.

        Args:
            request_id: ID of approval request
            approved: Whether approved
            approver: Who approved
            notes: Optional approval notes

        Returns:
            ApprovalDecision recorded
        """
        from datetime import datetime, timezone

        if request_id not in cls._pending_requests:
            logger.error(f"Approval request {request_id} not found")
            raise ValueError(f"Request {request_id} not found")

        request = cls._pending_requests[request_id]
        now = datetime.now(timezone.utc)

        # Check if SLA exceeded
        sla_expired = now > datetime.fromisoformat(request.sla_expires_at)
        if sla_expired:
            request.status = ApprovalStatus.SLA_EXCEEDED
            logger.warning(f"Approval request {request_id} SLA exceeded")

        # Record decision
        decision = ApprovalDecision(
            request_id=request_id,
            approved=approved,
            timestamp=now.isoformat(),
            approver=approver,
            notes=notes,
        )

        # Update request status
        if approved:
            request.status = ApprovalStatus.APPROVED
            request.approved_at = now.isoformat()
        else:
            request.status = ApprovalStatus.REJECTED

        cls._approval_history.append(decision)

        logger.info(
            f"Recorded approval decision for {request_id}: "
            f"{'approved' if approved else 'rejected'}"
        )

        return decision

    @classmethod
    def check_sla_compliance(cls) -> Dict[str, Any]:
        """Check SLA compliance for pending requests.

        Returns:
            Dict with compliance stats
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stats = {
            "total_pending": len(cls._pending_requests),
            "within_sla": 0,
            "sla_exceeded": 0,
            "at_risk": 0,  # <1 hour remaining
            "exceeded_requests": [],
        }

        for request_id, request in cls._pending_requests.items():
            sla_expires = datetime.fromisoformat(request.sla_expires_at)

            if now > sla_expires:
                stats["sla_exceeded"] += 1
                stats["exceeded_requests"].append(request_id)
                request.status = ApprovalStatus.SLA_EXCEEDED

                # Auto-escalate
                cls._escalate_request(request_id, "SLA exceeded")

            elif (sla_expires - now).total_seconds() < 3600:
                stats["at_risk"] += 1

            else:
                stats["within_sla"] += 1

        logger.info(f"SLA compliance check: {stats}")
        return stats

    @classmethod
    def _escalate_request(cls, request_id: str, reason: str) -> None:
        """Escalate approval request to governance.

        Args:
            request_id: Request to escalate
            reason: Reason for escalation
        """
        if request_id in cls._pending_requests:
            request = cls._pending_requests[request_id]
            request.status = ApprovalStatus.ESCALATED

            logger.warning(
                f"Escalated approval request {request_id} to governance: {reason}"
            )

    @classmethod
    def get_pending_requests(cls, tier: Optional[str] = None) -> List[ApprovalRequest]:
        """Get pending approval requests.

        Args:
            tier: Optional tier filter (T2, T3)

        Returns:
            List of pending ApprovalRequests
        """
        requests = list(cls._pending_requests.values())

        if tier:
            requests = [r for r in requests if r.tier == tier]

        return [r for r in requests if r.status == ApprovalStatus.PENDING]

    @classmethod
    def get_approval_history(cls) -> List[ApprovalDecision]:
        """Get approval decision history."""
        return cls._approval_history

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get approval routing metrics.

        Returns:
            Dict with approval metrics
        """
        from datetime import datetime, timezone

        history = cls._approval_history
        datetime.now(timezone.utc)

        # Calculate approval times
        approval_times = []
        for decision in history:
            if decision.approved:
                # Find corresponding request
                for request_id, request in cls._pending_requests.items():
                    if request.request_id == decision.request_id:
                        created = datetime.fromisoformat(request.created_at)
                        decided = datetime.fromisoformat(decision.timestamp)
                        duration = (decided - created).total_seconds()
                        approval_times.append(duration)
                        break

        avg_approval_time = (
            sum(approval_times) / len(approval_times) if approval_times else 0
        )

        metrics = {
            "total_requests": len(history),
            "approved": sum(1 for d in history if d.approved),
            "rejected": sum(1 for d in history if not d.approved),
            "approval_success_rate": (
                sum(1 for d in history if d.approved) / len(history)
                if history
                else 0
            ),
            "avg_approval_time_sec": avg_approval_time,
            "pending_count": len(cls._pending_requests),
            "sla_compliance": cls.check_sla_compliance(),
        }

        return metrics

    @classmethod
    def clear_history(cls) -> None:
        """Clear request and history for testing."""
        cls._pending_requests.clear()
        cls._approval_history.clear()
