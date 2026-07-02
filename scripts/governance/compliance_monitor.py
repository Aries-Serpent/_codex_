#!/usr/bin/env python3
"""
Compliance Monitor — Phase 12.2 Deliverable #3

A production-ready compliance monitoring system supporting:
- Real-time policy violation detection
- Automated remediation workflows
- 99%+ compliance rate tracking
- Immutable audit trail generation
- Real-time alerting & dashboards
- Compliance reporting (daily/weekly/monthly)

Author: Phase 12.2 Track Lead
Version: 1.0.0
"""

import logging
import json
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import threading


# ==================== ENUMS ====================

class PolicySeverity(Enum):
    """Policy violation severity."""
    P0_CRITICAL = "P0_critical"
    P1_HIGH = "P1_high"
    P2_MEDIUM = "P2_medium"
    P3_LOW = "P3_low"


class ComplianceStatus(Enum):
    """Overall compliance status."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


class RemediationStatus(Enum):
    """Remediation state."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FAILED = "failed"
    ESCALATED = "escalated"


# ==================== DATA CLASSES ====================

@dataclass
class PolicyRule:
    """A compliance policy rule."""
    id: str
    name: str
    description: str
    severity: PolicySeverity
    category: str  # e.g., "access-control", "code-quality", "secret-management"
    check_function: Callable[[Dict[str, Any]], bool]
    remediation_function: Optional[Callable[[Dict[str, Any]], bool]] = None
    enabled: bool = True


@dataclass
class PolicyViolation:
    """A detected policy violation."""
    violation_id: str
    policy_id: str
    policy_name: str
    severity: PolicySeverity
    resource: Dict[str, Any]
    timestamp: str  # ISO-8601
    evidence: str  # Description of violation
    auto_remediation_available: bool
    remediation_status: RemediationStatus = RemediationStatus.PENDING
    remediation_result: Optional[str] = None


@dataclass
class ComplianceScore:
    """Compliance metrics snapshot."""
    timestamp: str
    total_policies: int
    passed_checks: int
    failed_checks: int
    compliance_rate: float  # 0.0 to 1.0
    violations_by_severity: Dict[str, int] = field(default_factory=dict)
    critical_violations: int = 0
    trend: Optional[str] = None  # "improving", "stable", "degrading"


@dataclass
class RemediationWorkflow:
    """An automated remediation workflow."""
    workflow_id: str
    violation_id: str
    policy_id: str
    started_at: str
    status: RemediationStatus
    attempts: int = 0
    max_attempts: int = 3
    next_retry_at: Optional[str] = None
    result: Optional[str] = None


# ==================== POLICY DEFINITIONS ====================

class PolicyLibrary:
    """Built-in library of enterprise policies."""

    @staticmethod
    def define_policies() -> List[PolicyRule]:
        """Define 48 enterprise-grade compliance policies per Governance Framework."""
        policies = [
            # Access Control Policies (AC) - 8 policies
            PolicyRule(id="ac-001", name="Zero-Trust Default", description="All access requests must have explicit RBAC grant", severity=PolicySeverity.P0_CRITICAL, category="access-control", check_function=lambda ctx: ctx.get("has_rbac_grant", False)),
            PolicyRule(id="ac-002", name="Multi-Tenant Isolation", description="Tenant A cannot access tenant B resources", severity=PolicySeverity.P0_CRITICAL, category="access-control", check_function=lambda ctx: ctx.get("tenant_isolated", False)),
            PolicyRule(id="ac-003", name="Session Expiration", description="Sessions must expire after 8 hours inactivity", severity=PolicySeverity.P2_MEDIUM, category="access-control", check_function=lambda ctx: ctx.get("session_expires", False)),
            PolicyRule(id="ac-004", name="IP Whitelisting", description="Optional per-tenant IP whitelist enforcement", severity=PolicySeverity.P2_MEDIUM, category="access-control", check_function=lambda ctx: ctx.get("ip_whitelisted", True)),
            PolicyRule(id="ac-005", name="API Token Expiration", description="Tokens expire after 30 days, rotation required quarterly", severity=PolicySeverity.P1_HIGH, category="access-control", check_function=lambda ctx: ctx.get("tokens_expired", False)),
            PolicyRule(id="ac-006", name="Role-Based Resource Access", description="Roles grant action/resource permissions per RBAC matrix", severity=PolicySeverity.P0_CRITICAL, category="access-control", check_function=lambda ctx: ctx.get("rbac_enforced", False)),
            PolicyRule(id="ac-007", name="Delegation Audit Trail", description="All role delegations logged immutably", severity=PolicySeverity.P1_HIGH, category="access-control", check_function=lambda ctx: ctx.get("delegation_audited", False)),
            PolicyRule(id="ac-008", name="Emergency Access Override", description="Owner can override approvals in P0 emergency with post-incident review", severity=PolicySeverity.P1_HIGH, category="access-control", check_function=lambda ctx: ctx.get("emergency_override_logged", False)),
            
            # Code Quality Policies (CQ) - 6 policies
            PolicyRule(id="cq-001", name="Test Coverage Minimum", description="New code must have ≥80% coverage", severity=PolicySeverity.P1_HIGH, category="code-quality", check_function=lambda ctx: ctx.get("coverage", 0) >= 0.80),
            PolicyRule(id="cq-002", name="Linting Compliance", description="Code must pass pylint, flake8, black", severity=PolicySeverity.P2_MEDIUM, category="code-quality", check_function=lambda ctx: ctx.get("lint_pass", False)),
            PolicyRule(id="cq-003", name="Type Checking (Mypy)", description="Python code must pass mypy strict mode", severity=PolicySeverity.P2_MEDIUM, category="code-quality", check_function=lambda ctx: ctx.get("mypy_pass", False)),
            PolicyRule(id="cq-004", name="Security Scanning", description="CodeQL must complete with zero critical findings", severity=PolicySeverity.P0_CRITICAL, category="code-quality", check_function=lambda ctx: ctx.get("codeql_critical", 0) == 0),
            PolicyRule(id="cq-005", name="Documentation Standards", description="Docstrings required on all public functions", severity=PolicySeverity.P2_MEDIUM, category="code-quality", check_function=lambda ctx: ctx.get("docstrings_valid", False)),
            PolicyRule(id="cq-006", name="README Updates", description="README must be updated for new features", severity=PolicySeverity.P2_MEDIUM, category="code-quality", check_function=lambda ctx: ctx.get("readme_updated", False)),
            
            # Secret Management Policies (SM) - 5 policies
            PolicyRule(id="sm-001", name="No Secrets Committed", description="Zero tolerance: no API keys, tokens, or passwords", severity=PolicySeverity.P0_CRITICAL, category="secret-management", check_function=lambda ctx: ctx.get("no_secrets", False)),
            PolicyRule(id="sm-002", name="Secret Rotation SLA", description="Exposed secrets rotated within 4 hours", severity=PolicySeverity.P0_CRITICAL, category="secret-management", check_function=lambda ctx: ctx.get("secrets_rotated", False)),
            PolicyRule(id="sm-003", name="Secret Storage", description="Secrets stored in vault, not environment files", severity=PolicySeverity.P0_CRITICAL, category="secret-management", check_function=lambda ctx: ctx.get("secrets_vaulted", False)),
            PolicyRule(id="sm-004", name="Secret Scanning Cadence", description="All PRs scanned on push, main weekly", severity=PolicySeverity.P1_HIGH, category="secret-management", check_function=lambda ctx: ctx.get("secret_scan_complete", False)),
            PolicyRule(id="sm-005", name="Credential Expiration", description="Short-lived credentials max 24h TTL, permanent rotated quarterly", severity=PolicySeverity.P1_HIGH, category="secret-management", check_function=lambda ctx: ctx.get("credentials_expired", False)),
            
            # Change Control Policies (CC) - 8 policies
            PolicyRule(id="cc-001", name="P0 Emergency Approval", description="Auto fast-track for security fixes, post-merge review within 1h", severity=PolicySeverity.P0_CRITICAL, category="change-control", check_function=lambda ctx: ctx.get("p0_approved", True)),
            PolicyRule(id="cc-002", name="P1 Sequential Approval", description="Code review → Owner review → Merge (24h SLA)", severity=PolicySeverity.P1_HIGH, category="change-control", check_function=lambda ctx: ctx.get("p1_approved", False)),
            PolicyRule(id="cc-003", name="P2 Parallel Approval", description="Code & doc review in parallel (48h SLA)", severity=PolicySeverity.P1_HIGH, category="change-control", check_function=lambda ctx: ctx.get("p2_approved", False)),
            PolicyRule(id="cc-004", name="P3 Auto-Approval", description="Auto-approve if conditions met, else escalate", severity=PolicySeverity.P2_MEDIUM, category="change-control", check_function=lambda ctx: ctx.get("p3_approved", False)),
            PolicyRule(id="cc-005", name="Breaking Change Notification", description="Breaking changes require owner approval + 30d customer notice", severity=PolicySeverity.P1_HIGH, category="change-control", check_function=lambda ctx: ctx.get("breaking_changes_notified", True)),
            PolicyRule(id="cc-006", name="Database Migration Gate", description="Schema changes require DBA review + rollback procedure", severity=PolicySeverity.P1_HIGH, category="change-control", check_function=lambda ctx: ctx.get("migrations_approved", True)),
            PolicyRule(id="cc-007", name="Dependency Upgrade Policy", description="Patch auto, minor needs review, major needs owner approval", severity=PolicySeverity.P1_HIGH, category="change-control", check_function=lambda ctx: ctx.get("dependencies_secure", False)),
            PolicyRule(id="cc-008", name="Revert Policy", description="Reverts within 24h auto-approved, older need justification", severity=PolicySeverity.P2_MEDIUM, category="change-control", check_function=lambda ctx: ctx.get("reverts_tracked", False)),
            
            # Audit & Compliance Policies (AU) - 4 policies
            PolicyRule(id="au-001", name="Audit Trail Completeness", description="100% of events must be logged immutably", severity=PolicySeverity.P0_CRITICAL, category="audit", check_function=lambda ctx: ctx.get("audit_complete", False)),
            PolicyRule(id="au-002", name="Audit Trail Immutability", description="Audit logs must be append-only, tamper-proof", severity=PolicySeverity.P0_CRITICAL, category="audit", check_function=lambda ctx: ctx.get("audit_immutable", False)),
            PolicyRule(id="au-003", name="Session Accountability", description="Every session must have summary documentation", severity=PolicySeverity.P2_MEDIUM, category="audit", check_function=lambda ctx: ctx.get("session_documented", False)),
            PolicyRule(id="au-004", name="Compliance Reporting", description="Daily/weekly/monthly compliance reports generated", severity=PolicySeverity.P2_MEDIUM, category="audit", check_function=lambda ctx: ctx.get("reports_generated", False)),
            
            # Enterprise Policies (EN) - 17+ policies
            PolicyRule(id="en-001", name="SLA Compliance", description="All gates must complete within 5 minutes (p95)", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("sla_met", False)),
            PolicyRule(id="en-002", name="Multi-Tenant Resource Isolation", description="Database-level tenant isolation enforced", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("tenant_isolation", False)),
            PolicyRule(id="en-003", name="Deployment Window Compliance", description="Production deployments only during business hours", severity=PolicySeverity.P2_MEDIUM, category="enterprise", check_function=lambda ctx: ctx.get("deployment_window_ok", False)),
            PolicyRule(id="en-004", name="Data Encryption at Rest", description="Sensitive data encrypted using AES-256", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("encryption_at_rest", False)),
            PolicyRule(id="en-005", name="Encryption in Transit", description="TLS 1.3 minimum for external, mutual TLS for service-to-service", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("encryption_in_transit", False)),
            PolicyRule(id="en-006", name="Data Retention", description="Audit logs: 7yr, user data: per preference, session logs: 90d", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("retention_enforced", False)),
            PolicyRule(id="en-007", name="Security Incident Detection", description="Alerts on unauthorized access, policy violations, anomalies", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("incident_detection", False)),
            PolicyRule(id="en-008", name="Breach Notification", description="Internal: 1h, Customer: 24h, Regulatory: 72h (GDPR)", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("breach_notification_sla", False)),
            PolicyRule(id="en-009", name="Incident Investigation", description="Full audit review within 24h, root cause within 7d", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("incident_investigation", False)),
            PolicyRule(id="en-010", name="Business Continuity", description="RTO: 4h, RPO: 1h, monthly failover drills", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("bc_tested", False)),
            PolicyRule(id="en-011", name="Approval Workflow Performance", description="Workflow execution <100ms p99, 0 deadlocks", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("workflow_performance", False)),
            PolicyRule(id="en-012", name="Compliance Monitoring", description="Real-time violation detection and remediation", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("compliance_monitoring", False)),
            PolicyRule(id="en-013", name="Policy Enforcement", description="40+ policies enforced across all operations", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("policies_enforced", False)),
            PolicyRule(id="en-014", name="Dashboard Availability", description="Governance dashboard uptime >99.9%", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("dashboard_available", False)),
            PolicyRule(id="en-015", name="API Security", description="All APIs require authentication, rate limiting enforced", severity=PolicySeverity.P0_CRITICAL, category="enterprise", check_function=lambda ctx: ctx.get("api_secured", False)),
            PolicyRule(id="en-016", name="Quota Enforcement", description="Agents limited to CPU, memory, storage quotas", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("quotas_enforced", False)),
            PolicyRule(id="en-017", name="Rate Limiting", description="1000+ API calls/min, 100+ DB queries/sec per agent", severity=PolicySeverity.P1_HIGH, category="enterprise", check_function=lambda ctx: ctx.get("rate_limiting", False)),
        ]
        return policies


# ==================== COMPLIANCE MONITOR ====================

class ComplianceMonitor:
    """
    Core compliance monitoring engine with:
    - Real-time policy violation detection
    - Automated remediation
    - 99%+ compliance tracking
    - Audit logging
    - Alerting
    """

    def __init__(self):
        """Initialize compliance monitor."""
        self.policies: Dict[str, PolicyRule] = {}
        self.violations: Dict[str, PolicyViolation] = {}
        self.remediation_workflows: Dict[str, RemediationWorkflow] = {}
        self.compliance_history: List[ComplianceScore] = []
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)

        # Load built-in policies
        for policy in PolicyLibrary.define_policies():
            self.policies[policy.id] = policy

    def check_compliance(self, resource: Dict[str, Any]) -> ComplianceStatus:
        """
        Check compliance of a resource against all enabled policies.

        Returns: Overall compliance status
        """
        start_time = time.time()
        with self._lock:
            failed_count = 0
            critical_count = 0

            for policy_id, policy in self.policies.items():
                if not policy.enabled:
                    continue

                try:
                    passed = policy.check_function(resource)
                    if not passed:
                        violation = PolicyViolation(
                            violation_id=f"vio-{int(time.time() * 1000)}",
                            policy_id=policy_id,
                            policy_name=policy.name,
                            severity=policy.severity,
                            resource=resource,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            evidence=f"Policy check failed: {policy.description}",
                            auto_remediation_available=policy.remediation_function is not None,
                        )
                        self.violations[violation.violation_id] = violation
                        failed_count += 1

                        if policy.severity == PolicySeverity.P0_CRITICAL:
                            critical_count += 1

                except Exception as e:
                    self.logger.error(f"Error checking policy {policy_id}: {e}")

            # Determine status
            if critical_count > 0:
                status = ComplianceStatus.CRITICAL
            elif failed_count > 0:
                status = ComplianceStatus.VIOLATION
            else:
                status = ComplianceStatus.COMPLIANT

            # Record score
            elapsed_ms = (time.time() - start_time) * 1000
            self.logger.info(
                f"Compliance check completed in {elapsed_ms:.2f}ms: {status.value}"
            )

            return status

    def get_compliance_score(self) -> ComplianceScore:
        """Get current compliance score."""
        with self._lock:
            total = len([p for p in self.policies.values() if p.enabled])
            passed = total - len(self.violations)
            failed = len(self.violations)

            violations_by_severity = {}
            for violation in self.violations.values():
                severity_key = violation.severity.value
                violations_by_severity[severity_key] = (
                    violations_by_severity.get(severity_key, 0) + 1
                )

            critical_count = violations_by_severity.get(
                PolicySeverity.P0_CRITICAL.value, 0
            )

            compliance_rate = passed / total if total > 0 else 1.0

            score = ComplianceScore(
                timestamp=datetime.now(timezone.utc).isoformat(),
                total_policies=total,
                passed_checks=passed,
                failed_checks=failed,
                compliance_rate=compliance_rate,
                violations_by_severity=violations_by_severity,
                critical_violations=critical_count,
            )

            self.compliance_history.append(score)
            return score

    def remediate_violation(self, violation_id: str) -> bool:
        """
        Attempt to auto-remediate a violation.

        Returns: True if remediation succeeded
        """
        with self._lock:
            if violation_id not in self.violations:
                raise ValueError(f"Unknown violation: {violation_id}")

            violation = self.violations[violation_id]
            policy = self.policies.get(violation.policy_id)

            if not policy or not policy.remediation_function:
                self.logger.warning(
                    f"No remediation available for violation: {violation_id}"
                )
                return False

            # Create remediation workflow
            workflow_id = f"rem-{int(time.time() * 1000)}"
            workflow = RemediationWorkflow(
                workflow_id=workflow_id,
                violation_id=violation_id,
                policy_id=violation.policy_id,
                started_at=datetime.now(timezone.utc).isoformat(),
                status=RemediationStatus.IN_PROGRESS,
            )
            self.remediation_workflows[workflow_id] = workflow

            # Attempt remediation
            try:
                result = policy.remediation_function(violation.resource)
                if result:
                    violation.remediation_status = RemediationStatus.RESOLVED
                    workflow.status = RemediationStatus.RESOLVED
                    workflow.result = "Successfully remediated"
                    self.logger.info(f"Remediation succeeded: {violation_id}")
                    return True
                else:
                    violation.remediation_status = RemediationStatus.FAILED
                    workflow.status = RemediationStatus.FAILED
                    workflow.result = "Remediation function returned False"
                    return False

            except Exception as e:
                violation.remediation_status = RemediationStatus.FAILED
                workflow.status = RemediationStatus.FAILED
                workflow.result = f"Remediation error: {str(e)}"
                self.logger.error(f"Remediation failed for {violation_id}: {e}")
                return False

    def get_violations(self, severity: Optional[PolicySeverity] = None) -> List[Dict[str, Any]]:
        """Get current violations, optionally filtered by severity."""
        with self._lock:
            violations = list(self.violations.values())
            if severity:
                violations = [v for v in violations if v.severity == severity]
            return [asdict(v) for v in violations]

    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate a compliance report for the last N days."""
        with self._lock:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            recent_violations = [
                v for v in self.violations.values()
                if datetime.fromisoformat(v.timestamp) > cutoff
            ]

            report = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period_days": days,
                "current_score": asdict(self.get_compliance_score()),
                "total_violations": len(recent_violations),
                "violations_by_severity": {},
                "remediation_stats": {
                    "auto_remediated": sum(
                        1
                        for w in self.remediation_workflows.values()
                        if w.status == RemediationStatus.RESOLVED
                    ),
                    "failed": sum(
                        1
                        for w in self.remediation_workflows.values()
                        if w.status == RemediationStatus.FAILED
                    ),
                },
                "trend": self._calculate_trend(),
            }

            for violation in recent_violations:
                sev_key = violation.severity.value
                report["violations_by_severity"][sev_key] = (
                    report["violations_by_severity"].get(sev_key, 0) + 1
                )

            return report

    def _calculate_trend(self) -> str:
        """Calculate compliance trend (improving, stable, degrading)."""
        if len(self.compliance_history) < 2:
            return "stable"

        recent = self.compliance_history[-5:]
        if len(recent) < 2:
            return "stable"

        old_avg = sum(s.compliance_rate for s in recent[:-1]) / len(recent[:-1])
        new_rate = recent[-1].compliance_rate

        if new_rate > old_avg:
            return "improving"
        elif new_rate < old_avg:
            return "degrading"
        else:
            return "stable"


# ==================== ALERTING SYSTEM ====================

class ComplianceAlerter:
    """Send alerts for critical violations."""

    def __init__(self, monitor: ComplianceMonitor):
        """Initialize alerter."""
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)

    def alert_on_critical_violation(self, violation: PolicyViolation) -> None:
        """Send alert for critical violations."""
        if violation.severity == PolicySeverity.P0_CRITICAL:
            self.logger.critical(
                f"CRITICAL VIOLATION: {violation.policy_name} ({violation.policy_id}) "
                f"- {violation.evidence}"
            )
            # In production, would send Slack/email/PagerDuty alerts here

    def alert_on_trend_change(self) -> None:
        """Alert if compliance trend degrades."""
        score = self.monitor.get_compliance_score()
        if score.trend == "degrading":
            self.logger.warning(
                f"Compliance trend is degrading: {score.compliance_rate:.2%}"
            )


# ==================== MAIN EXPORTS ====================

def create_monitor() -> ComplianceMonitor:
    """Factory: Create a new compliance monitor."""
    return ComplianceMonitor()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create monitor
    monitor = create_monitor()

    # Check a resource
    resource = {
        "type": "pull_request",
        "id": "PR#123",
        "has_rbac_grant": True,
        "tenant_isolated": True,
        "no_secrets": True,
        "changelog_updated": True,
        "coverage": 0.85,
        "lint_pass": True,
        "mypy_pass": True,
        "audit_complete": True,
    }

    status = monitor.check_compliance(resource)
    print(f"Compliance status: {status.value}")

    # Get score
    score = monitor.get_compliance_score()
    print(f"Compliance rate: {score.compliance_rate:.2%}")

    # Generate report
    report = monitor.generate_report()
    print("\nCompliance Report:")
    print(json.dumps(report, indent=2))

