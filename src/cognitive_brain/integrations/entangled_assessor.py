"""
Entangled Compliance-Security Assessor.

Coordinates compliance and security audits via quantum-inspired entanglement,
reducing redundant actions and improving decision consistency.

Use Cases:
- Compliance violation → trigger correlated security scan
- Security issue → reassess compliance implications
- Joint decision-making for PII + secret exposure
"""

from dataclasses import dataclass
from typing import Any, Optional

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceAssessment,
    QuantumComplianceAssessor,
)
from cognitive_brain.quantum.entanglement import EntanglementManager


@dataclass
class EntangledAssessmentResult:
    """
    Result of entangled compliance + security assessment.

    Attributes:
        compliance: Compliance assessment result
        security: Security assessment result (mocked for now)
        correlation: Measured correlation between decisions
        redundancy_avoided: Whether redundant action was avoided
        pair_id: ID of the entangled pair used
    """

    compliance: ComplianceAssessment
    security: dict[str, Any]  # Mock security result
    correlation: float
    redundancy_avoided: bool
    pair_id: str

    @property
    def compliance_decision(self) -> Any:
        """Alias for compliance.decision for backward compatibility."""
        return self.compliance.decision if self.compliance else None

    @property
    def security_assessment(self) -> dict[str, Any]:
        """Alias for security for backward compatibility."""
        return self.security


class MockSecurityScanner:
    """Mock security scanner for testing entangled assessments."""

    def scan_for_secrets(self, audit: AuditResult) -> dict[str, Any]:
        """
        Mock security scan.

        Returns dict with decision matching compliance for high risk.
        """
        # For high risk compliance issues, security usually agrees
        if audit.risk_level == "high":
            # Check violations for security-sensitive keywords
            violations_str = " ".join(audit.violations).lower()
            if (
                "secret" in violations_str
                or "credential" in violations_str
                or "pii" in violations_str
            ):
                decision = "BLOCK"  # High correlation with compliance
            else:
                decision = "MONITOR"
        else:
            decision = "ALLOW"

        return {
            "decision": decision,
            "secrets_found": any(
                "secret" in v.lower() or "credential" in v.lower() for v in audit.violations
            ),
            "confidence": 0.85,
            "scan_time_ms": 5.0,
        }


class EntangledComplianceSecurityAssessor:
    """
    Coordinates compliance and security audits via entanglement.

    Benefits:
    - Reduced redundant scans (30% reduction target)
    - Correlated decision-making (>0.80 correlation)
    - Faster response time

    Rayleigh Metrics:
    - NA: 2.0 (two-agent coordination)
    - Correlation: > 0.80
    - Latency: < 10ms overhead
    """

    def __init__(
        self,
        compliance_assessor: QuantumComplianceAssessor = None,
        security_scanner: Optional[MockSecurityScanner] = None,
        entanglement_mgr: EntanglementManager = None,
        entanglement_manager: EntanglementManager = None,
        config: Any | None = None,  # Accept but ignore for compatibility
    ):
        """
        Initialize entangled assessor.

        Args:
            entanglement_mgr: EntanglementManager instance (or use entanglement_manager)
            entanglement_manager: Alternative name for entanglement_mgr
            compliance_assessor: QuantumComplianceAssessor instance
            security_scanner: Security scanner (defaults to mock)
            config: Optional config (for compatibility, not used)
        """
        # Support both parameter names
        mgr = entanglement_mgr or entanglement_manager
        if mgr is None:
            raise ValueError("Either entanglement_mgr or entanglement_manager must be provided")

        self.entanglement = mgr
        self.compliance = compliance_assessor
        self.security = security_scanner or MockSecurityScanner()
        self.pair_id: Optional[str] = None
        self.redundant_actions_avoided = 0
        self.total_assessments = 0
        self._initialized_correlation = False

    def setup_entanglement(self, correlation_strength: float = 0.85) -> str:
        """
        Create entanglement between compliance + security agents.

        Args:
            correlation_strength: Target correlation coefficient (0-1)

        Returns:
            Pair ID of created entanglement
        """
        self.pair_id = self.entanglement.create_entanglement(
            "compliance-checker", "security-scan", correlation_strength
        )
        return self.pair_id

    def assess_with_entanglement(self, audit: AuditResult) -> EntangledAssessmentResult:
        """
        Perform entangled compliance + security assessment.

        Process:
        1. Compliance check (agent1)
        2. Collapse entangled security state (agent2)
        3. Validate correlation
        4. Avoid redundant scan if possible

        Args:
            audit: Audit result to assess

        Returns:
            EntangledAssessmentResult with both assessments
        """
        if not self.pair_id:
            raise ValueError("Entanglement not set up. Call setup_entanglement() first.")

        self.total_assessments += 1

        # Step 1: Compliance assessment
        compliance_result = self.compliance.assess_compliance(audit)
        compliance_decision = compliance_result.decision

        # Step 2: Check entangled state for security decision
        suggested_security_decision = self.entanglement.collapse_entangled_state(
            self.pair_id, compliance_decision
        )

        # Step 3: Decide if full security scan is needed
        # High correlation means we can trust the suggested decision
        # But we need at least 2 observations to measure correlation
        try:
            correlation = self.entanglement.measure_correlation(self.pair_id)
        except ValueError:
            # Not enough observations yet, set low correlation
            correlation = 0.0

        redundancy_avoided = False

        if correlation > 0.75 and suggested_security_decision:
            # Trust entangled state, avoid full scan
            security_result = {
                "decision": suggested_security_decision,
                "secrets_found": False,
                "confidence": 0.80,
                "scan_time_ms": 0.5,  # Fast, no full scan
                "from_entanglement": True,
            }
            redundancy_avoided = True
            self.redundant_actions_avoided += 1
        else:
            # Perform full security scan
            security_result = self.security.scan_for_secrets(audit)
            security_result["from_entanglement"] = False

        # Step 4: Update entanglement with observed correlation
        self.entanglement.update_correlation(
            self.pair_id, compliance_decision, security_result["decision"]
        )
        self._initialized_correlation = True

        return EntangledAssessmentResult(
            compliance=compliance_result,
            security=security_result,
            correlation=correlation,
            redundancy_avoided=redundancy_avoided,
            pair_id=self.pair_id,
        )

    def assess_entangled(self, audit: AuditResult) -> "EntangledAssessmentResult":
        """Alias for assess_with_entanglement for backward compatibility."""
        return self.assess_with_entanglement(audit)

    def get_redundancy_reduction(self) -> float:
        """
        Calculate percentage of redundant actions avoided.

        Returns:
            Redundancy reduction ratio (0.0 to 1.0)
        """
        if self.total_assessments == 0:
            return 0.0
        return self.redundant_actions_avoided / self.total_assessments

    def get_statistics(self) -> dict[str, Any]:
        """
        Get assessment statistics.

        Returns:
            Dict with statistics
        """
        correlation = 0.0
        if self.pair_id and self._initialized_correlation:
            try:
                correlation = self.entanglement.measure_correlation(self.pair_id)
            except ValueError:
                # Not enough observations yet
                correlation = 0.0

        return {
            "total_assessments": self.total_assessments,
            "redundant_actions_avoided": self.redundant_actions_avoided,
            "redundancy_reduction": self.get_redundancy_reduction(),
            "pair_id": self.pair_id,
            "correlation": correlation,
        }
