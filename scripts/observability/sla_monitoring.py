#!/usr/bin/env python3
"""
Approval SLA Monitoring & Integration

Integrates telemetry collector with D2.2 approval service.
Implements real-time SLA monitoring, escalation triggering, and compliance reporting.

Phase 12 Wave 2 - D3.2 Deliverable
"""

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SLAStatus(str, Enum):
    """SLA status tracking"""
    MET = "met"
    APPROACHING = "approaching"  # >80% of SLA
    BREACHED = "breached"


@dataclass
class SLAViolation:
    """Record of an SLA violation"""
    approval_id: str
    policy_category: str
    policy_id: str
    latency_seconds: float
    sla_seconds: float
    exceeded_by_seconds: float
    timestamp: datetime
    escalation_triggered: bool = False


class SLAMonitor:
    """
    Real-time SLA monitoring and compliance tracking.
    
    Monitors approval request latencies against SLA thresholds.
    Triggers escalations and generates compliance reports.
    Integrates with approval service state changes.
    """
    
    # SLA Thresholds (in seconds)
    THRESHOLDS = {
        "D": (4 * 3600, 12 * 3600),      # Deployment: 4h per-stage, 12h total
        "S": (4 * 3600, 12 * 3600),      # Security: 4h per-stage, 12h total
        "R": (4 * 3600, 12 * 3600),      # Resource: 4h per-stage, 12h total
        "C": (4 * 3600, 12 * 3600),      # Config: 4h per-stage, 12h total
        "G": (4 * 3600, 12 * 3600),      # Capability: 4h per-stage, 12h total
        "I": (2 * 3600, 2 * 3600),       # Incident: 2h emergency
        "A": (8 * 3600, 24 * 3600),      # Audit: 8h per-stage, 24h total
        "E": (4 * 3600, None),           # Escalation: 4h per level
    }
    
    def __init__(
        self,
        telemetry_collector,
        escalation_callback: Optional[Callable[[str, str, str], None]] = None,
    ):
        """
        Initialize SLA monitor.
        
        Args:
            telemetry_collector: ApprovalTelemetryCollector instance
            escalation_callback: Optional callback for escalation triggers
                               Signature: (approval_id, policy_category, reason) -> None
        """
        self.collector = telemetry_collector
        self.escalation_callback = escalation_callback
        self.lock = threading.RLock()
        
        # Track in-flight approvals for SLA monitoring
        self.in_flight: Dict[str, Dict[str, Any]] = {}
        
        # SLA violation log
        self.violations: List[SLAViolation] = []
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "sla_met": 0,
            "sla_breached": 0,
            "sla_approaching": 0,
            "escalations_triggered": 0,
        }
        
        logger.info("SLAMonitor initialized")
    
    def track_approval_request(
        self,
        approval_id: str,
        policy_category: str,
        policy_id: str,
        submitted_at: datetime,
    ) -> None:
        """Start tracking an approval request's SLA."""
        with self.lock:
            self.in_flight[approval_id] = {
                "policy_category": policy_category,
                "policy_id": policy_id,
                "submitted_at": submitted_at,
                "stages": [],
                "sla_status": SLAStatus.MET.value,
            }
            self.stats["total_requests"] += 1
    
    def record_stage_decision(
        self,
        approval_id: str,
        stage: int,
        decision_time_seconds: float,
        policy_category: str,
    ) -> Dict[str, Any]:
        """
        Record a decision on an approval stage.
        
        Returns:
            {
                "sla_status": "met|approaching|breached",
                "exceeded_by": float (0 if met),
                "escalation_triggered": bool,
            }
        """
        with self.lock:
            if approval_id not in self.in_flight:
                logger.warning(f"Unknown approval {approval_id} in stage decision")
                return {"sla_status": "unknown", "exceeded_by": 0}
            
            # Get SLA threshold
            per_stage_sla, total_sla = self.THRESHOLDS.get(policy_category, (14400, 86400))
            
            # Check per-stage SLA
            if decision_time_seconds > per_stage_sla:
                status = SLAStatus.BREACHED
                exceeded = decision_time_seconds - per_stage_sla
                self.stats["sla_breached"] += 1
                
                # Log violation
                violation = SLAViolation(
                    approval_id=approval_id,
                    policy_category=policy_category,
                    policy_id=self.in_flight[approval_id]["policy_id"],
                    latency_seconds=decision_time_seconds,
                    sla_seconds=per_stage_sla,
                    exceeded_by_seconds=exceeded,
                    timestamp=datetime.now(timezone.utc),
                )
                self.violations.append(violation)
                
                # Trigger escalation if configured
                escalation_triggered = False
                if self.escalation_callback:
                    self.escalation_callback(
                        approval_id,
                        policy_category,
                        f"Stage {stage} SLA breached by {exceeded:.0f}s",
                    )
                    escalation_triggered = True
                    self.stats["escalations_triggered"] += 1
                
                result = {
                    "sla_status": SLAStatus.BREACHED.value,
                    "exceeded_by": exceeded,
                    "escalation_triggered": escalation_triggered,
                }
            
            elif decision_time_seconds > per_stage_sla * 0.8:
                status = SLAStatus.APPROACHING
                self.stats["sla_approaching"] += 1
                result = {
                    "sla_status": SLAStatus.APPROACHING.value,
                    "exceeded_by": 0,
                    "escalation_triggered": False,
                }
            
            else:
                status = SLAStatus.MET
                self.stats["sla_met"] += 1
                result = {
                    "sla_status": SLAStatus.MET.value,
                    "exceeded_by": 0,
                    "escalation_triggered": False,
                }
            
            # Update in-flight record
            self.in_flight[approval_id]["stages"].append({
                "stage": stage,
                "decision_time_seconds": decision_time_seconds,
                "sla_status": status.value,
            })
            self.in_flight[approval_id]["sla_status"] = status.value
            
            return result
    
    def complete_approval(self, approval_id: str) -> None:
        """Mark approval as complete; remove from in-flight tracking."""
        with self.lock:
            if approval_id in self.in_flight:
                del self.in_flight[approval_id]
    
    def get_sla_compliance_report(self) -> Dict[str, Any]:
        """Generate SLA compliance report by policy category."""
        with self.lock:
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_requests": self.stats["total_requests"],
                "sla_met_count": self.stats["sla_met"],
                "sla_breached_count": self.stats["sla_breached"],
                "sla_approaching_count": self.stats["sla_approaching"],
                "escalations_triggered": self.stats["escalations_triggered"],
                "sla_compliance_pct": (
                    (self.stats["sla_met"] / max(1, self.stats["total_requests"])) * 100
                ),
                "violations": [],
                "by_category": {},
            }
            
            # Violations in detail
            report["violations"] = [
                {
                    "approval_id": v.approval_id,
                    "policy_category": v.policy_category,
                    "policy_id": v.policy_id,
                    "latency_seconds": v.latency_seconds,
                    "sla_seconds": v.sla_seconds,
                    "exceeded_by_seconds": v.exceeded_by_seconds,
                    "timestamp": v.timestamp.isoformat(),
                }
                for v in self.violations[-100:]  # Last 100 violations
            ]
            
            # Breakdown by category
            violations_by_cat = {}
            for v in self.violations:
                cat = v.policy_category
                if cat not in violations_by_cat:
                    violations_by_cat[cat] = []
                violations_by_cat[cat].append(v)
            
            for cat, violations in violations_by_cat.items():
                report["by_category"][cat] = {
                    "violations": len(violations),
                    "avg_exceeded_by_seconds": (
                        sum(v.exceeded_by_seconds for v in violations) / len(violations)
                    ),
                    "max_exceeded_by_seconds": max(v.exceeded_by_seconds for v in violations),
                }
            
            return report
    
    def get_in_flight_approvals(self) -> List[Dict[str, Any]]:
        """Get all in-flight approvals and their current SLA status."""
        with self.lock:
            return list(self.in_flight.values())


class ComplianceReporter:
    """
    Generates compliance reports for audit and governance.
    
    Tracks SLA compliance over time.
    Identifies patterns and trends.
    Produces reportable metrics for compliance teams.
    """
    
    def __init__(self, sla_monitor: SLAMonitor):
        """Initialize reporter."""
        self.sla_monitor = sla_monitor
        self.reports_generated: List[Dict[str, Any]] = []
    
    def generate_hourly_report(self) -> Dict[str, Any]:
        """Generate hourly compliance report."""
        report = {
            "period": "1h",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sla_compliance": self.sla_monitor.get_sla_compliance_report(),
            "metric_snapshots": {},
        }
        
        self.reports_generated.append(report)
        
        # Keep last 24 reports
        if len(self.reports_generated) > 24:
            self.reports_generated.pop(0)
        
        return report
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily compliance report."""
        if len(self.reports_generated) < 24:
            hourly_data = self.reports_generated
        else:
            hourly_data = self.reports_generated[-24:]
        
        compliance_data = [h["sla_compliance"] for h in hourly_data]
        
        report = {
            "period": "24h",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "aggregate_sla_compliance_pct": (
                sum(c["sla_compliance_pct"] for c in compliance_data) / len(compliance_data)
            ),
            "total_violations_24h": sum(c["sla_breached_count"] for c in compliance_data),
            "escalations_24h": sum(c["escalations_triggered"] for c in compliance_data),
            "by_category": self._aggregate_by_category(compliance_data),
            "recommendations": self._generate_recommendations(compliance_data),
        }
        
        return report
    
    def _aggregate_by_category(self, compliance_data: List[Dict]) -> Dict[str, Any]:
        """Aggregate compliance data by policy category."""
        by_cat = {}
        
        for data in compliance_data:
            for cat, cat_data in data["by_category"].items():
                if cat not in by_cat:
                    by_cat[cat] = {
                        "total_violations": 0,
                        "avg_exceeded_seconds": [],
                        "max_exceeded_seconds": 0,
                    }
                
                by_cat[cat]["total_violations"] += cat_data["violations"]
                by_cat[cat]["avg_exceeded_seconds"].append(cat_data["avg_exceeded_by_seconds"])
                by_cat[cat]["max_exceeded_seconds"] = max(
                    by_cat[cat]["max_exceeded_seconds"],
                    cat_data["max_exceeded_by_seconds"],
                )
        
        # Average the exceeded seconds
        for cat, data in by_cat.items():
            if data["avg_exceeded_seconds"]:
                data["avg_exceeded_seconds"] = (
                    sum(data["avg_exceeded_seconds"]) / len(data["avg_exceeded_seconds"])
                )
            else:
                data["avg_exceeded_seconds"] = 0
        
        return by_cat
    
    def _generate_recommendations(self, compliance_data: List[Dict]) -> List[str]:
        """Generate recommendations based on compliance trends."""
        recommendations = []
        
        avg_compliance = (
            sum(c["sla_compliance_pct"] for c in compliance_data) / len(compliance_data)
        )
        
        if avg_compliance < 95:
            recommendations.append(
                "SLA compliance <95%. Review approval process and authority capacity."
            )
        
        total_violations = sum(c["sla_breached_count"] for c in compliance_data)
        if total_violations > 10:
            recommendations.append(
                f"High violation rate ({total_violations} in 24h). "
                "Escalate to approval authority managers."
            )
        
        return recommendations


class ApprovalServiceIntegration:
    """
    Integration hook for D2.2 Approval Service.
    
    Listens to approval state changes and updates telemetry.
    Coordinates SLA monitoring with approval workflow engine.
    """
    
    def __init__(self, telemetry_collector, sla_monitor: SLAMonitor):
        """Initialize integration."""
        self.collector = telemetry_collector
        self.sla_monitor = sla_monitor
        self.logger = logging.getLogger(__name__)
    
    def on_request_submitted(
        self,
        approval_id: str,
        policy_id: str,
        policy_category: str,
        requester_id: str,
        requester_role: str,
        sla_seconds: float,
    ) -> None:
        """Handle approval request submission event."""
        self.collector.record_approval_request(
            approval_id=approval_id,
            policy_id=policy_id,
            policy_category=policy_category,
            requester_id=requester_id,
            requester_role=requester_role,
            sla_seconds=sla_seconds,
        )
        
        self.sla_monitor.track_approval_request(
            approval_id=approval_id,
            policy_category=policy_category,
            policy_id=policy_id,
            submitted_at=datetime.now(timezone.utc),
        )
        
        self.logger.info(f"Approval request tracked: {approval_id}")
    
    def on_decision_made(
        self,
        approval_id: str,
        policy_id: str,
        policy_category: str,
        approver_id: str,
        approver_role: str,
        decision: str,
        decision_time_seconds: float,
        stage: int,
        sla_seconds: float,
    ) -> None:
        """Handle approval decision event."""
        sla_met, sla_status = self.collector.record_approval_decision(
            approval_id=approval_id,
            policy_id=policy_id,
            policy_category=policy_category,
            approver_id=approver_id,
            approver_role=approver_role,
            decision=decision,
            decision_time_seconds=decision_time_seconds,
            stage=stage,
            sla_seconds=sla_seconds,
        )
        
        result = self.sla_monitor.record_stage_decision(
            approval_id=approval_id,
            stage=stage,
            decision_time_seconds=decision_time_seconds,
            policy_category=policy_category,
        )
        
        self.logger.info(
            f"Decision recorded for {approval_id}: {sla_status} "
            f"({decision_time_seconds:.0f}s vs {sla_seconds:.0f}s SLA)"
        )
    
    def on_approval_completed(self, approval_id: str) -> None:
        """Handle approval completion event."""
        self.sla_monitor.complete_approval(approval_id)
        self.logger.info(f"Approval completed: {approval_id}")


if __name__ == "__main__":
    # Quick integration test
    logging.basicConfig(level=logging.INFO)
    
    from approval_telemetry_collector import ApprovalTelemetryCollector
    
    collector = ApprovalTelemetryCollector()
    
    def escalation_callback(approval_id, policy_cat, reason):
        print(f"ESCALATION: {approval_id} ({policy_cat}) - {reason}")
    
    sla_monitor = SLAMonitor(collector, escalation_callback=escalation_callback)
    integration = ApprovalServiceIntegration(collector, sla_monitor)
    reporter = ComplianceReporter(sla_monitor)
    
    # Simulate approval workflow
    integration.on_request_submitted(
        approval_id="apr-001",
        policy_id="D-001",
        policy_category="D",
        requester_id="agent-orchestrator",
        requester_role="release-operator",
        sla_seconds=14400,
    )
    
    # Simulate decision (within SLA)
    integration.on_decision_made(
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
    
    # Generate report
    report = reporter.generate_hourly_report()
    print(f"\nCompliance Report:\n{report}")
